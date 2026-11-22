
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.producer import Producer
from app.models.product import Product
from app.models.product_review import ProductReview
from app.models.order_item import OrderItem
from app.models.category import Category
from app.models.user import User

from app.services.product_service import get_my_products
from app.services.producer_service import (
    create_producer_profile,
    get_producer_profile,
    update_producer_profile,
    get_producer_orders,
    mark_pickup_ready
)

from app.dependencies import get_db
from app.schemas.producer import (
    ProducerProfileCreate,
    ProducerProfileResponse
)
from app.utils.session import require_roles


router = APIRouter(
    prefix="/producer",
    tags=["Producer"]
)

templates = Jinja2Templates(
    directory="app/templates"
)


# ==========================================
# PRODUCER PROFILE PAGE
# ==========================================

@router.get("/profile/page")
def producer_profile_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("producer"))
):
    profile = get_producer_profile(db, user.id)

    # Jika profil belum dibuat, tampilkan form pembuatan.
    if not profile:
        return templates.TemplateResponse(
            request=request,
            name="producer_profile_form.html",
            context={
                "user": user
            }
        )

    # Jika profil sudah ada, tampilkan halaman profil.
    return templates.TemplateResponse(
        request=request,
        name="producer_profile.html",
        context={
            "user": user,
            "producer": profile
        }
    )


# ==========================================
# CREATE PRODUCER PROFILE
# ==========================================

@router.post(
    "/profile",
    response_model=ProducerProfileResponse
)
def create_profile(
    data: ProducerProfileCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("producer"))
):
    try:
        return create_producer_profile(db, user, data)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ==========================================
# GET PRODUCER PROFILE API
# ==========================================

@router.get(
    "/profile",
    response_model=ProducerProfileResponse
)
def read_profile(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("producer"))
):
    profile = get_producer_profile(db, user.id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profil toko belum dibuat"
        )

    return profile


# ==========================================
# UPDATE PRODUCER PROFILE
# ==========================================

@router.put(
    "/profile",
    response_model=ProducerProfileResponse
)
def update_profile(
    data: ProducerProfileCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("producer"))
):
    try:
        return update_producer_profile(db, user.id, data)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ==========================================
# PRODUCER ORDER PAGE
# ==========================================

@router.get("/orders/page")
def producer_orders_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("producer"))
):
    try:
        orders = get_producer_orders(db, user.id)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    return templates.TemplateResponse(
        request=request,
        name="producer_orders.html",
        context={
            "user": user,
            "orders": orders
        }
    )


# ==========================================
# MARK PICKUP READY
# ==========================================

@router.post("/orders/{pickup_id}/ready")
def producer_mark_order_ready(
    pickup_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("producer"))
):
    try:
        mark_pickup_ready(db, user.id, pickup_id)

        return RedirectResponse(
            url="/producer/orders/page",
            status_code=303
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ==========================================
# PRODUCER PRODUCT REVIEWS PAGE
# ==========================================

@router.get("/reviews/page")
def producer_reviews_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("producer"))
):
    producer = get_producer_profile(db, user.id)

    if not producer:
        return RedirectResponse(
            url="/producer/profile/page",
            status_code=303
        )

    products = db.query(Product).filter(
        Product.producer_id == producer.id
    ).all()

    product_data = []

    for product in products:
        reviews = (
            db.query(ProductReview, OrderItem)
            .join(
                OrderItem,
                ProductReview.order_item_id == OrderItem.id
            )
            .filter(
                ProductReview.product_id == product.id
            )
            .order_by(ProductReview.created_at.desc())
            .all()
        )

        rating_data = db.query(
            func.avg(ProductReview.rating),
            func.count(ProductReview.id)
        ).filter(
            ProductReview.product_id == product.id
        ).first()

        average_rating = float(rating_data[0] or 0)
        review_count = rating_data[1] or 0

        product_data.append({
            "product": product,
            "average_rating": average_rating,
            "review_count": review_count,
            "reviews": [
                {
                    "review": review,
                    "order_item": order_item
                }
                for review, order_item in reviews
            ]
        })

    return templates.TemplateResponse(
        request=request,
        name="producer_reviews.html",
        context={
            "user": user,
            "producer": producer,
            "products": product_data
        }
    )


# ==========================================
# PRODUCER PRODUCT MANAGEMENT PAGE
# ==========================================

@router.get("/products/page")
def producer_products_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("producer"))
):
    profile = get_producer_profile(db, user.id)

    if not profile:
        return RedirectResponse(
            url="/producer/profile/page",
            status_code=303
        )

    products = get_my_products(db, user)

    return templates.TemplateResponse(
        request=request,
        name="producer_products.html",
        context={
            "user": user,
            "products": products
        }
    )


# ==========================================
# PRODUCER ADD PRODUCT PAGE
# ==========================================

@router.get("/products/page/add")
def producer_add_product_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("producer"))
):
    profile = get_producer_profile(db, user.id)

    if not profile:
        return RedirectResponse(
            url="/producer/profile/page",
            status_code=303
        )

    categories = db.query(Category).filter(
        Category.is_active == True
    ).order_by(Category.name.asc()).all()

    return templates.TemplateResponse(
        request=request,
        name="producer_product_form.html",
        context={
            "user": user,
            "categories": categories,
            "product": None,
            "page_title": "Tambah Produk"
        }
    )


# ==========================================
# PRODUCER EDIT PRODUCT PAGE
# ==========================================

@router.get("/products/page/{product_id}/edit")
def producer_edit_product_page(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("producer"))
):
    profile = get_producer_profile(db, user.id)

    if not profile:
        return RedirectResponse(
            url="/producer/profile/page",
            status_code=303
        )

    products = get_my_products(db, user)

    product = next(
        (
            item for item in products
            if item["id"] == product_id
        ),
        None
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Produk tidak ditemukan"
        )

    normalized_units = []

    for unit in product.get("units", []):
        normalized_unit = dict(unit)

        for key in ("conversion_factor", "price"):
            value = normalized_unit.get(key)

            if isinstance(value, Decimal):
                normalized_unit[key] = float(value)

        normalized_units.append(normalized_unit)

    product["units"] = normalized_units

    categories = db.query(Category).filter(
        Category.is_active == True
    ).order_by(Category.name.asc()).all()

    current_category = db.query(Category).filter(
        Category.id == product["category_id"]
    ).first()

    if (
        current_category
        and not current_category.is_active
    ):
        categories.append(current_category)

    return templates.TemplateResponse(
        request=request,
        name="producer_product_form.html",
        context={
            "user": user,
            "categories": categories,
            "product": product,
            "page_title": "Edit Produk"
        }
    )
