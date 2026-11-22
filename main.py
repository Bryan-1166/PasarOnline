
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from app.models.customer_profile import CustomerProfile

from app.routers import (
    auth,
    dashboard,
    producer,
    product,
    catalog,
    cart,
    checkout,
    driver,
    customer_order,
    customer
)


load_dotenv()

app = FastAPI(
    title="PasarOnline API",
    description="API Marketplace PasarOnline",
    version="1.0.0"
)

app.mount(
    "/public",
    StaticFiles(directory="public"),
    name="public"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET"),
    session_cookie="pasaronline_session",
    max_age=60 * 60 * 24,
    same_site="lax",
    https_only=False
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(producer.router)
app.include_router(product.router)
app.include_router(catalog.router)
app.include_router(cart.router)
app.include_router(checkout.router)
app.include_router(driver.router)
app.include_router(customer_order.router)
app.include_router(customer.router)

@app.get("/")
def home():
    return {
        "message": "Selamat datang di PasarOnline!"
    }
