
from pydantic import BaseModel, Field


class ProducerProfileCreate(BaseModel):
    shop_name: str = Field(min_length=3, max_length=150)
    phone: str = Field(min_length=8, max_length=20)
    description: str | None = None

    market_name: str = Field(min_length=3, max_length=150)
    block: str | None = Field(default=None, max_length=50)
    stall_number: str = Field(min_length=1, max_length=50)
    floor: str | None = Field(default=None, max_length=50)


class ProducerProfileResponse(BaseModel):
    id: int
    user_id: int
    shop_name: str
    phone: str
    description: str | None
    market_name: str
    block: str | None
    stall_number: str
    floor: str | None

    class Config:
        from_attributes = True
