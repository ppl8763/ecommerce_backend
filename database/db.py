from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI= "mongodb+srv://Amit:Amit@cluster0.modflkm.mongodb.net/"
client = AsyncIOMotorClient(MONGO_URI)
db = client["ecommerce_db"]
user_collection = db["user"]
product_collection = db["products"]
cart_collection = db["cart"]
order_collection = db["order"]