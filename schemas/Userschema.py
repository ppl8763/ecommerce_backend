from pydantic import BaseModel,EmailStr
from typing import List
from datetime import datetime
class Address(BaseModel):
    street:str
    city:str
    state:str
    pincode:str
    region:str

class Usersignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    role: str = "user"
    is_active: bool = True
    is_verified: bool = False
    address: List[Address]
    
class Userlogin(BaseModel):
    email:EmailStr
    password:str