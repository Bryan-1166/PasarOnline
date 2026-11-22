
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.utils.session import require_roles
from app.schemas.cart import CartItemAdd, CartItemUpdate

from app.services.cart_service import (
    get_cart,
    add_cart_item,
    update_cart_item,
    remove_cart_item
)


router = APIRouter(
    prefix="/customer/cart",
    tags=["Customer Cart"]
)

templates = Jinja2Templates(directory="app/templates")


# ==========================================
# HALAMAN HTML KERANJANG
# ==========================================

@router.get("/page")
def cart_page(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    cart = get_cart(db, user)

    return templates.TemplateResponse(
        request=request,
        name="customer_cart.html",
        context={
            "cart": cart,
            "user": user
        }
    )


# ==========================================
# READ: MELIHAT DATA KERANJANG
# ==========================================

@router.get("/")
def view_cart(
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    return get_cart(db, user)


# ==========================================
# CREATE: MENAMBAHKAN PRODUK
# ==========================================

@router.post("/items", status_code=status.HTTP_201_CREATED)
def add_item(
    data: CartItemAdd,
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    try:
        return add_cart_item(db, user, data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==========================================
# UPDATE: MENGUBAH JUMLAH PRODUK
# ==========================================

@router.put("/items/{item_id}")
def edit_item(
    item_id: int,
    data: CartItemUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    try:
        return update_cart_item(db, user, item_id, data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==========================================
# DELETE: MENGHAPUS PRODUK
# ==========================================

@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    try:
        return remove_cart_item(db, user, item_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
