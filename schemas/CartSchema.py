from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)

class AddToCart(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)