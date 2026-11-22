
from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemAdd(BaseModel):
    product_unit_id: int = Field(gt=0)
    quantity: Decimal = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: Decimal = Field(gt=0)
