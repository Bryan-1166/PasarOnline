
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import UploadFile, File
from app.dependencies import get_db
from app.utils.session import require_roles
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductUnitsUpdate
)
from app.services.product_service import (
    create_product,
    get_my_products,
    update_product,
    delete_product,
    update_product_units,
    update_product_image,
)


router = APIRouter(
    prefix="/producer/products",
    tags=["Producer Products"]
)


# ==========================================
# CREATE: Menambahkan produk
# ==========================================

@router.post("/", status_code=status.HTTP_201_CREATED)
def add_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("producer"))
):
    try:
        return create_product(db, user, data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==========================================
# READ: Melihat semua produk milik penjual
# ==========================================

@router.get("/")
def list_my_products(
    db: Session = Depends(get_db),
    user=Depends(require_roles("producer"))
):
    try:
        return get_my_products(db, user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==========================================
# UPDATE: Mengedit produk
# ==========================================

@router.put("/{product_id}")
def edit_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("producer"))
):
    try:
        return update_product(db, user, product_id, data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==========================================
# DELETE: Menonaktifkan produk
# ==========================================

@router.delete("/{product_id}")
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("producer"))
):
    try:
        return delete_product(db, user, product_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==========================================
# UPDATE: Mengelola harga dan pilihan satuan
# ==========================================

@router.put("/{product_id}/units")
def edit_product_units(
    product_id: int,
    data: ProductUnitsUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("producer"))
):
    try:
        return update_product_units(
            db,
            user,
            product_id,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{product_id}/image")
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_roles("producer"))
):
    try:
        return await update_product_image(
            db, user, product_id, file
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
