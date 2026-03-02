from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
load_dotenv() 
MONGO_URI= os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["ecommerce_db"]
user_collection = db["user"]
product_collection = db["products"]
cart_collection = db["cart"]
order_collection = db["order"]