
from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Literal


class UserRegister(BaseModel):
    email: EmailStr

    full_name: str = Field(
        min_length=3,
        max_length=150
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=128
    )

    role: Literal["user", "producer", "driver"]

    phone: str | None = Field(
        default=None,
        max_length=20
    )

    @model_validator(mode="after")
    def check_registration(self):
        if self.password != self.confirm_password:
            raise ValueError("Konfirmasi password tidak cocok")

        if self.role == "driver" and not self.phone:
            raise ValueError("Nomor telepon wajib diisi untuk driver")

        if self.phone and not self.phone.strip():
            raise ValueError("Nomor telepon tidak boleh kosong")

        return self


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True
