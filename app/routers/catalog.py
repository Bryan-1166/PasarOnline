
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import Request
from fastapi.templating import Jinja2Templates
from app.dependencies import get_db
from app.utils.session import require_roles
from app.services.catalog_service import get_catalog_products


router = APIRouter(
    prefix="/customer/catalog",
    tags=["Customer Catalog"]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/products")
def list_catalog_products(
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    return get_catalog_products(db)

@router.get("/dashboard")
def customer_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    products = get_catalog_products(db)

    return templates.TemplateResponse(
        request=request,
        name="customer_dashboard.html",
        context={
            "products": products,
            "user": user
        }
    )