
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.product_unit import ProductUnit
from app.models.producer import Producer


def get_or_create_cart(db: Session, user):
    cart = db.query(Cart).filter(
        Cart.user_id == user.id,
        Cart.status == "active"
    ).first()

    if not cart:
        cart = Cart(
            user_id=user.id,
            status="active"
        )
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


def get_cart(db: Session, user):
    cart = get_or_create_cart(db, user)

    items = (
        db.query(CartItem, ProductUnit, Product, Producer)
        .join(ProductUnit, CartItem.product_unit_id == ProductUnit.id)
        .join(Product, ProductUnit.product_id == Product.id)
        .join(Producer, Product.producer_id == Producer.id)
        .filter(
            CartItem.cart_id == cart.id,
            Product.is_active == True,
            ProductUnit.is_active == True
        )
        .all()
    )

    result = []
    subtotal = Decimal("0")

    for item, unit, product, producer in items:
        item_subtotal = Decimal(str(unit.price)) * Decimal(str(item.quantity))
        subtotal += item_subtotal

        result.append({
            "id": item.id,
            "product_id": product.id,
            "product_name": product.name,
            "image": product.image,
            "producer_name": producer.shop_name,
            "product_unit_id": unit.id,
            "unit_name": unit.unit_name,
            "conversion_factor": unit.conversion_factor,
            "quantity": item.quantity,
            "unit_price": unit.price,
            "subtotal": item_subtotal
        })

    return {
        "cart_id": cart.id,
        "items": result,
        "total_items": len(result),
        "subtotal": subtotal
    }


def add_cart_item(db: Session, user, data):
    cart = get_or_create_cart(db, user)

    unit = db.query(ProductUnit).join(
        Product,
        ProductUnit.product_id == Product.id
    ).filter(
        ProductUnit.id == data.product_unit_id,
        ProductUnit.is_active == True,
        Product.is_active == True
    ).first()

    if not unit:
        raise ValueError("Produk atau satuan tidak ditemukan")

    product = db.query(Product).filter(
        Product.id == unit.product_id
    ).first()

    requested_quantity = Decimal(str(data.quantity))
    conversion_factor = Decimal(str(unit.conversion_factor))
    required_stock = requested_quantity * conversion_factor

    if required_stock > Decimal(str(product.stock_quantity)):
        raise ValueError("Stok produk tidak mencukupi")

    try:
        cart_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_unit_id == unit.id
        ).first()

        if cart_item:
            new_quantity = (
                Decimal(str(cart_item.quantity)) + requested_quantity
            )

            total_required = new_quantity * conversion_factor

            if total_required > Decimal(str(product.stock_quantity)):
                raise ValueError("Stok produk tidak mencukupi")

            cart_item.quantity = new_quantity
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_unit_id=unit.id,
                quantity=requested_quantity
            )
            db.add(cart_item)

        db.commit()
        db.refresh(cart_item)

        return get_cart(db, user)

    except Exception:
        db.rollback()
        raise


def update_cart_item(db: Session, user, item_id: int, data):
    cart = get_or_create_cart(db, user)

    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not item:
        raise ValueError("Item keranjang tidak ditemukan")

    unit = db.query(ProductUnit).filter(
        ProductUnit.id == item.product_unit_id,
        ProductUnit.is_active == True
    ).first()

    if not unit:
        raise ValueError("Satuan produk tidak tersedia")

    product = db.query(Product).filter(
        Product.id == unit.product_id,
        Product.is_active == True
    ).first()

    if not product:
        raise ValueError("Produk tidak tersedia")

    new_quantity = Decimal(str(data.quantity))
    required_stock = (
        new_quantity * Decimal(str(unit.conversion_factor))
    )

    if required_stock > Decimal(str(product.stock_quantity)):
        raise ValueError("Stok produk tidak mencukupi")

    try:
        item.quantity = new_quantity
        db.commit()

        return get_cart(db, user)

    except Exception:
        db.rollback()
        raise


def remove_cart_item(db: Session, user, item_id: int):
    cart = get_or_create_cart(db, user)

    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not item:
        raise ValueError("Item keranjang tidak ditemukan")

    db.delete(item)
    db.commit()

    return get_cart(db, user)
