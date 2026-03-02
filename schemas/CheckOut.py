from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int

class OrderCreate(BaseModel):
    shipping_address: dict