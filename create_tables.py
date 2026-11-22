from app.database import Base, engine
import app.models
from app.models.user import User
from app.models.producer import Producer
from app.models.driver import Driver
from app.models.category import Category
from app.models.product import Product
from app.models.product_unit import ProductUnit
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.delivery import Delivery
from app.models.delivery_pickup import DeliveryPickup
from app.models.order_status_history import OrderStatusHistory

try:
    Base.metadata.create_all(bind=engine)
    print("Semua tabel berhasil dibuat!")

except Exception as e:
    print("Gagal membuat tabel!")
    print("Error:", e)