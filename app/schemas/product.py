
from pydantic import BaseModel, Field
from decimal import Decimal


class ProductUnitCreate(BaseModel):
    unit_name: str = Field(min_length=1, max_length=50)
    conversion_factor: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)


class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None
    base_unit: str = Field(min_length=1, max_length=50)
    stock_quantity: Decimal = Field(ge=0)
    units: list[ProductUnitCreate] = Field(min_length=1)


class ProductUpdate(BaseModel):
    category_id: int
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None
    base_unit: str = Field(min_length=1, max_length=50)
    stock_quantity: Decimal = Field(ge=0)


class ProductUnitResponse(BaseModel):
    id: int
    unit_name: str
    conversion_factor: Decimal
    price: Decimal
    is_active: bool

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    producer_id: int
    category_id: int
    name: str
    description: str | None
    image: str | None
    base_unit: str
    stock_quantity: Decimal
    is_active: bool
    units: list[ProductUnitResponse] = []

    class Config:
        from_attributes = True


class ProductUnitManage(BaseModel):
    id: int | None = None
    unit_name: str = Field(min_length=1, max_length=50)
    conversion_factor: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)
    is_active: bool = True


class ProductUnitsUpdate(BaseModel):
    # Boleh kosong ketika semua pilihan satuan dihapus.
    units: list[ProductUnitManage] = Field(default_factory=list)
