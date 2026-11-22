
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_unit import ProductUnit
from app.models.category import Category
from app.models.producer import Producer

from fastapi import UploadFile
from app.utils.image_upload import save_product_image


# ==========================================
# HELPER: Mengubah data produk menjadi dictionary
# ==========================================

def product_to_dict(product, units):
    return {
        "id": product.id,
        "producer_id": product.producer_id,
        "category_id": product.category_id,
        "name": product.name,
        "description": product.description,
        "image": product.image,
        "base_unit": product.base_unit,
        "stock_quantity": product.stock_quantity,
        "is_active": product.is_active,
        "units": [
            {
                "id": unit.id,
                "unit_name": unit.unit_name,
                "conversion_factor": unit.conversion_factor,
                "price": unit.price,
                "is_active": unit.is_active,
            }
            for unit in units
        ],
    }


# ==========================================
# CREATE: Menambahkan produk
# ==========================================

def create_product(db: Session, user, data):
    producer = db.query(Producer).filter(
        Producer.user_id == user.id
    ).first()

    if not producer:
        raise ValueError("Profil penjual belum dibuat")

    category = db.query(Category).filter(
        Category.id == data.category_id,
        Category.is_active == True
    ).first()

    if not category:
        raise ValueError("Kategori tidak ditemukan atau tidak aktif")

    unit_names = [
        unit.unit_name.strip().lower()
        for unit in data.units
    ]

    if len(unit_names) != len(set(unit_names)):
        raise ValueError("Nama satuan tidak boleh duplikat")

    try:
        product = Product(
            producer_id=producer.id,
            category_id=data.category_id,
            name=data.name,
            description=data.description,
            base_unit=data.base_unit,
            stock_quantity=data.stock_quantity,
            is_active=True,
        )

        db.add(product)
        db.flush()

        units = []

        for unit_data in data.units:
            unit = ProductUnit(
                product_id=product.id,
                unit_name=unit_data.unit_name.strip(),
                conversion_factor=unit_data.conversion_factor,
                price=unit_data.price,
                is_active=True,
            )

            db.add(unit)
            units.append(unit)

        db.commit()
        db.refresh(product)

        for unit in units:
            db.refresh(unit)

        return product_to_dict(product, units)

    except Exception:
        db.rollback()
        raise


# ==========================================
# READ: Melihat produk milik penjual
# ==========================================

def get_my_products(db: Session, user):
    producer = db.query(Producer).filter(
        Producer.user_id == user.id
    ).first()

    if not producer:
        raise ValueError("Profil penjual belum dibuat")

    products = db.query(Product).filter(
        Product.producer_id == producer.id,
        Product.is_active == True
    ).order_by(Product.id.desc()).all()

    result = []

    for product in products:
        units = db.query(ProductUnit).filter(
            ProductUnit.product_id == product.id,
            ProductUnit.is_active == True
        ).all()

        result.append(
            product_to_dict(product, units)
        )

    return result


# ==========================================
# UPDATE: Mengedit informasi produk
# ==========================================

def update_product(db: Session, user, product_id, data):
    producer = db.query(Producer).filter(
        Producer.user_id == user.id
    ).first()

    if not producer:
        raise ValueError("Profil penjual belum dibuat")

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.producer_id == producer.id,
        Product.is_active == True
    ).first()

    if not product:
        raise ValueError("Produk tidak ditemukan")

    category = db.query(Category).filter(
        Category.id == data.category_id,
        Category.is_active == True
    ).first()

    if not category:
        raise ValueError("Kategori tidak ditemukan atau tidak aktif")

    try:
        product.category_id = data.category_id
        product.name = data.name
        product.description = data.description
        product.base_unit = data.base_unit
        product.stock_quantity = data.stock_quantity

        db.commit()
        db.refresh(product)

        units = db.query(ProductUnit).filter(
            ProductUnit.product_id == product.id,
            ProductUnit.is_active == True
        ).all()

        return product_to_dict(product, units)

    except Exception:
        db.rollback()
        raise


# ==========================================
# DELETE: Menonaktifkan produk
# ==========================================

def delete_product(db: Session, user, product_id):
    producer = db.query(Producer).filter(
        Producer.user_id == user.id
    ).first()

    if not producer:
        raise ValueError("Profil penjual belum dibuat")

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.producer_id == producer.id,
        Product.is_active == True
    ).first()

    if not product:
        raise ValueError("Produk tidak ditemukan")

    try:
        product.is_active = False

        units = db.query(ProductUnit).filter(
            ProductUnit.product_id == product.id
        ).all()

        for unit in units:
            unit.is_active = False

        db.commit()

        return {
            "message": "Produk berhasil dinonaktifkan"
        }

    except Exception:
        db.rollback()
        raise


# ==========================================
# UPDATE: Mengelola satuan produk
# ==========================================

def update_product_units(db: Session, user, product_id, data):
    producer = db.query(Producer).filter(
        Producer.user_id == user.id
    ).first()

    if not producer:
        raise ValueError("Profil penjual belum dibuat")

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.producer_id == producer.id,
        Product.is_active == True
    ).first()

    if not product:
        raise ValueError("Produk tidak ditemukan")

    # Validasi nama satuan yang aktif.
    unit_names = [
        unit.unit_name.strip().lower()
        for unit in data.units
        if unit.is_active
    ]

    if len(unit_names) != len(set(unit_names)):
        raise ValueError("Nama satuan tidak boleh duplikat")

    # Ambil semua satuan yang pernah dibuat untuk produk ini.
    existing_units = db.query(ProductUnit).filter(
        ProductUnit.product_id == product.id
    ).all()

    existing_units_by_id = {
        unit.id: unit
        for unit in existing_units
    }

    try:
        # Nonaktifkan satuan lama terlebih dahulu.
        # Satuan yang dikirim dari form akan diperbarui
        # sesuai status is_active masing-masing.
        for unit in existing_units:
            unit.is_active = False

        for unit_data in data.units:

            if unit_data.id is not None:
                # Memperbarui satuan yang sudah ada.
                unit = existing_units_by_id.get(
                    unit_data.id
                )

                if not unit:
                    raise ValueError(
                        "Pilihan satuan tidak ditemukan pada produk ini"
                    )

                unit.unit_name = unit_data.unit_name.strip()
                unit.conversion_factor = unit_data.conversion_factor
                unit.price = unit_data.price
                unit.is_active = unit_data.is_active

            else:
                # Menambahkan satuan baru.
                unit = ProductUnit(
                    product_id=product.id,
                    unit_name=unit_data.unit_name.strip(),
                    conversion_factor=unit_data.conversion_factor,
                    price=unit_data.price,
                    is_active=unit_data.is_active,
                )

                db.add(unit)

        db.commit()
        db.refresh(product)

        # Ambil kembali satuan yang masih aktif.
        updated_units = db.query(ProductUnit).filter(
            ProductUnit.product_id == product.id,
            ProductUnit.is_active == True
        ).all()

        return product_to_dict(
            product,
            updated_units
        )

    except Exception:
        db.rollback()
        raise


# ==========================================
# UPDATE: Mengubah gambar produk
# ==========================================

async def update_product_image(
    db: Session,
    user,
    product_id: int,
    file: UploadFile
):
    producer = db.query(Producer).filter(
        Producer.user_id == user.id
    ).first()

    if not producer:
        raise ValueError("Profil penjual belum dibuat")

    product = db.query(Product).filter(
        Product.id == product_id,
        Product.producer_id == producer.id,
        Product.is_active == True
    ).first()

    if not product:
        raise ValueError("Produk tidak ditemukan")

    # Simpan gambar ke folder public/images/products.
    image_path = await save_product_image(file)

    try:
        product.image = image_path

        db.commit()
        db.refresh(product)

        units = db.query(ProductUnit).filter(
            ProductUnit.product_id == product.id,
            ProductUnit.is_active == True
        ).all()

        return product_to_dict(
            product,
            units
        )

    except Exception:
        db.rollback()
        raise
