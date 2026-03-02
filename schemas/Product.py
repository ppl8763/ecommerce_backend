from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from fastapi import Form

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    discount_price: Optional[float] = Field(default=None, gt=0)
    stock: int = Field(ge=0)
    category: str
    brand: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        discount_price: Optional[float] = Form(None),
        stock: int = Form(...),
        category: str = Form(...),
        brand: Optional[str] = Form(None),
    ):
        return cls(
            name=name,
            description=description,
            price=price,
            discount_price=discount_price,
            stock=stock,
            category=category,
            brand=brand,
        )
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    stock: Optional[int] = None

    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        category: Optional[str] = Form(None),
        brand: Optional[str] = Form(None),
        price: Optional[float] = Form(None),
        discount_price: Optional[float] = Form(None),
        stock: Optional[int] = Form(None)
    ):
        return cls(
            name=name,
            description=description,
            category=category,
            brand=brand,
            price=price,
            discount_price=discount_price,
            stock=stock
        )