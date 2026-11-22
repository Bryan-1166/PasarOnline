
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from app.dependencies import get_db
from app.models.user import User
from app.models.producer import Producer
from app.models.driver import Driver
from app.models.product import Product
from app.models.order import Order
from app.utils.session import require_roles
from app.models.category import Category
from app.models.payment import Payment
from app.models.delivery import Delivery
from app.models.category import Category
from app.models.product_review import ProductReview

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/user")
def user_dashboard(
    user: User = Depends(require_roles("user"))
):
    return {
        "message": "Selamat datang di Dashboard Pelanggan",
        "nama": user.full_name,
        "role": user.role
    }


@router.get("/producer")
def producer_dashboard(
    user: User = Depends(require_roles("producer"))
):
    return {
        "message": "Selamat datang di Dashboard Penjual",
        "nama": user.full_name,
        "role": user.role
    }


@router.get("/driver")
def driver_dashboard(
    user: User = Depends(require_roles("driver"))
):
    return {
        "message": "Selamat datang di Dashboard Kurir",
        "nama": user.full_name,
        "role": user.role
    }


# Dashboard Admin versi JSON (endpoint lama tetap dipertahankan)
@router.get("/admin")
def admin_dashboard(
    user: User = Depends(require_roles("admin"))
):
    return {
        "message": "Selamat datang di Dashboard Admin",
        "nama": user.full_name,
        "role": user.role
    }


# Dashboard Admin versi halaman website
@router.get("/admin/page")
def admin_dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    total_users = db.query(User).count()

    total_customers = db.query(User).filter(
        User.role == "user"
    ).count()

    total_producers = db.query(Producer).count()

    total_drivers = db.query(Driver).count()

    total_products = db.query(Product).count()

    total_orders = db.query(Order).count()

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "user": user,
            "total_users": total_users,
            "total_customers": total_customers,
            "total_producers": total_producers,
            "total_drivers": total_drivers,
            "total_products": total_products,
            "total_orders": total_orders
        }
    )


# Halaman Manajemen Akun
@router.get("/admin/accounts")
def admin_accounts_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    accounts = db.query(User).order_by(User.id.asc()).all()

    return templates.TemplateResponse(
        request=request,
        name="admin_accounts.html",
        context={
            "user": user,
            "accounts": accounts
        }
    )


# Aktifkan / Nonaktifkan Akun
@router.post("/admin/accounts/{account_id}/toggle")
def toggle_account(
    account_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    account = db.query(User).filter(
        User.id == account_id
    ).first()

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Akun tidak ditemukan"
        )

    # Admin tidak boleh menonaktifkan akunnya sendiri
    if account.id == user.id:
        raise HTTPException(
            status_code=400,
            detail="Anda tidak dapat menonaktifkan akun sendiri"
        )

    account.is_active = not account.is_active

    db.commit()

    return RedirectResponse(
        url="/dashboard/admin/accounts",
        status_code=303
    )

# Halaman Manajemen Producer
@router.get("/admin/producers")
def admin_producers_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    producers = (
        db.query(Producer, User)
        .join(User, Producer.user_id == User.id)
        .order_by(Producer.id.asc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin_producers.html",
        context={
            "user": user,
            "producers": producers
        }
    )

@router.get("/admin/drivers")
def admin_drivers_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    drivers = (
        db.query(Driver, User)
        .join(User, Driver.user_id == User.id)
        .order_by(Driver.id.asc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin_drivers.html",
        context={
            "user": user,
            "drivers": drivers
        }
    )

@router.get("/admin/products")
def admin_products_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    products = (
        db.query(Product, Producer, Category)
        .join(Producer, Product.producer_id == Producer.id)
        .join(Category, Product.category_id == Category.id)
        .order_by(Product.id.asc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin_products.html",
        context={
            "user": user,
            "products": products
        }
    )


@router.get("/admin/orders")
def admin_orders_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    orders = (
        db.query(Order, User, Payment, Delivery)
        .join(User, Order.user_id == User.id)
        .outerjoin(Payment, Payment.order_id == Order.id)
        .outerjoin(Delivery, Delivery.order_id == Order.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin_orders.html",
        context={
            "user": user,
            "orders": orders
        }
    )

@router.get("/admin/categories")
def admin_categories_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    categories = (
        db.query(Category)
        .order_by(Category.id.asc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin_categories.html",
        context={
            "user": user,
            "categories": categories
        }
    )


@router.post("/admin/categories/{category_id}/toggle")
def toggle_category_status(
    category_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Kategori tidak ditemukan"
        )

    category.is_active = not category.is_active

    db.commit()

    return RedirectResponse(
        url="/dashboard/admin/categories",
        status_code=303
    )

@router.get("/admin/reviews")
def admin_reviews_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin"))
):
    reviews = (
        db.query(ProductReview, Product, User)
        .join(Product, ProductReview.product_id == Product.id)
        .join(User, ProductReview.user_id == User.id)
        .order_by(ProductReview.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin_reviews.html",
        context={
            "user": user,
            "reviews": reviews
        }
    )