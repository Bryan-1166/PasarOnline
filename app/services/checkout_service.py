
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import secrets

from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.product_unit import ProductUnit
from app.models.producer import Producer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment


DELIVERY_FEE_RATE = Decimal("0.03")


def money(value):
    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def generate_order_number():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_code = secrets.token_hex(3).upper()
    return f"PO-{timestamp}-{random_code}"


def generate_va_number():
    return "880" + "".join(
        str(secrets.randbelow(10)) for _ in range(13)
    )


def create_checkout(db: Session, user):
    cart = db.query(Cart).filter(
        Cart.user_id == user.id,
        Cart.status == "active"
    ).first()

    if not cart:
        raise ValueError("Keranjang belum tersedia")

    cart_rows = (
        db.query(CartItem, ProductUnit, Product, Producer)
        .join(
            ProductUnit,
            CartItem.product_unit_id == ProductUnit.id
        )
        .join(
            Product,
            ProductUnit.product_id == Product.id
        )
        .join(
            Producer,
            Product.producer_id == Producer.id
        )
        .filter(CartItem.cart_id == cart.id)
        .all()
    )

    if not cart_rows:
        raise ValueError("Keranjang masih kosong")

    try:
        # Validasi produk dan satuan
        for item, unit, product, producer in cart_rows:
            if not product.is_active or not unit.is_active:
                raise ValueError(
                    f"Produk {product.name} sudah tidak tersedia"
                )

            if item.quantity <= 0:
                raise ValueError("Jumlah produk tidak valid")

        # Hitung total kebutuhan stok untuk setiap produk.
        required_stock_by_product = {}

        for item, unit, product, producer in cart_rows:
            required = (
                Decimal(str(item.quantity))
                * Decimal(str(unit.conversion_factor))
            )

            required_stock_by_product[product.id] = (
                required_stock_by_product.get(
                    product.id,
                    Decimal("0")
                ) + required
            )

        # Kunci baris produk selama transaksi untuk menghindari
        # dua checkout mengurangi stok produk secara bersamaan.
        product_ids = sorted(required_stock_by_product.keys())

        locked_products = (
            db.query(Product)
            .filter(Product.id.in_(product_ids))
            .order_by(Product.id)
            .with_for_update()
            .all()
        )

        products_by_id = {
            product.id: product
            for product in locked_products
        }

        for product_id, required_stock in required_stock_by_product.items():
            product = products_by_id.get(product_id)

            if not product or not product.is_active:
                raise ValueError("Produk sudah tidak tersedia")

            available_stock = Decimal(str(product.stock_quantity))

            if required_stock > available_stock:
                raise ValueError(
                    f"Stok {product.name} tidak mencukupi. "
                    f"Stok tersedia: {available_stock}, "
                    f"kebutuhan: {required_stock}"
                )

        # Hitung subtotal pesanan
        subtotal = Decimal("0")

        for item, unit, product, producer in cart_rows:
            line_subtotal = (
                Decimal(str(unit.price))
                * Decimal(str(item.quantity))
            )
            subtotal += line_subtotal

        subtotal = money(subtotal)
        delivery_fee = money(subtotal * DELIVERY_FEE_RATE)
        total_amount = money(subtotal + delivery_fee)

        # Buat pesanan utama
        order = Order(
            order_number=generate_order_number(),
            user_id=user.id,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            status="waiting_payment"
        )

        db.add(order)
        db.flush()

        # Simpan detail pesanan dengan snapshot data produk
        for item, unit, product, producer in cart_rows:
            line_subtotal = money(
                Decimal(str(unit.price))
                * Decimal(str(item.quantity))
            )

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_unit_id=unit.id,
                producer_id=producer.id,
                product_name=product.name,
                producer_name=producer.shop_name,
                unit_name=unit.unit_name,
                quantity=item.quantity,
                unit_price=unit.price,
                subtotal=line_subtotal
            )

            db.add(order_item)

        # Kurangi stok dalam satuan dasar produk
        for product_id, required_stock in required_stock_by_product.items():
            product = products_by_id[product_id]
            product.stock_quantity = (
                Decimal(str(product.stock_quantity)) - required_stock
            )

        # Buat pembayaran Virtual Account simulasi
        payment = Payment(
            order_id=order.id,
            payment_method="virtual_account",
            va_number=generate_va_number(),
            amount=total_amount,
            status="waiting_confirmation"
        )

        db.add(payment)

        # Kosongkan keranjang setelah pesanan berhasil dibuat
        for item, unit, product, producer in cart_rows:
            db.delete(item)

        db.commit()

        db.refresh(order)
        db.refresh(payment)

        return {
            "message": "Checkout berhasil",
            "order": {
                "id": order.id,
                "order_number": order.order_number,
                "subtotal": float(order.subtotal),
                "delivery_fee": float(order.delivery_fee),
                "total_amount": float(order.total_amount),
                "status": order.status,
                "created_at": order.created_at
            },
            "payment": {
                "payment_method": payment.payment_method,
                "va_number": payment.va_number,
                "amount": float(payment.amount),
                "status": payment.status
            }
        }

    except Exception:
        db.rollback()
        raise
