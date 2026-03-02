from fastapi import APIRouter
from fastapi import APIRouter,Depends,HTTPException
from schemas.CheckOut import OrderItem,OrderCreate
from middleware.auth import get_current_user,role_required
from database.db import cart_collection,product_collection,order_collection
from datetime import datetime
from bson import ObjectId
import razorpay
import os
import hmac
import hashlib
from dotenv import load_dotenv
from fastapi import Request

load_dotenv()

client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))
router = APIRouter()

@router.post("/checkout")
async def checkout(cur_user=Depends(get_current_user)):

    user_id = str(cur_user["_id"])
    address = cur_user["address"]

    cart = await cart_collection.find_one({"user_id": user_id})

    if not cart or not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_items = []
    total_amount = 0

    for item in cart["items"]:
        product = await product_collection.find_one(
            {"_id": ObjectId(item["product_id"])}
        )

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product["stock"] < item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"{product['name']} out of stock"
            )

        price = product["price"]
        total_amount += price * item["quantity"]

        order_items.append({
            "product_id": str(product["_id"]),
            "name": product["name"],
            "price": price,
            "quantity": item["quantity"]
        })

    # Create Razorpay Order
    razorpay_order = client.order.create({
        "amount": int(total_amount * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    order_data = {
        "user_id": user_id,
        "items": order_items,
        "total_amount": total_amount,
        "shipping_address": address,
        "payment_status": "pending",
        "order_status": "pending",
        "razorpay_order_id": razorpay_order["id"],
        "created_at": datetime.utcnow()
    }

    result = await order_collection.insert_one(order_data)

    return {
        "order_id": str(result.inserted_id),
        "razorpay_order_id": razorpay_order["id"],
        "amount": razorpay_order["amount"],
        "key": os.getenv("RAZORPAY_KEY_ID")
    }
@router.get("/total_revnue")
async def get_all():
    res = await order_collection.find().to_list(length=None)

    for item in res:
        item["_id"]= str(item["_id"])
    return res
@router.post("/verify-payment")
async def verify_payment(data: dict, cur_user=Depends(get_current_user)):

    razorpay_order_id = data["razorpay_order_id"]
    razorpay_payment_id = data["razorpay_payment_id"]
    razorpay_signature = data["razorpay_signature"]

    # Verify signature
    generated_signature = hmac.new(
        bytes(os.getenv("RAZORPAY_KEY_SECRET"), "utf-8"),
        bytes(f"{razorpay_order_id}|{razorpay_payment_id}", "utf-8"),
        hashlib.sha256
    ).hexdigest()

    if generated_signature != razorpay_signature:
        raise HTTPException(status_code=400, detail="Payment verification failed")

    order = await order_collection.find_one(
        {"razorpay_order_id": razorpay_order_id}
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Deduct stock
    for item in order["items"]:
        await product_collection.update_one(
            {"_id": ObjectId(item["product_id"])},
            {"$inc": {"stock": -item["quantity"]}}
        )

    # Clear cart
    await cart_collection.update_one(
        {"user_id": order["user_id"]},
        {"$set": {"items": []}}
    )

    # Mark order as paid
    await order_collection.update_one(
        {"_id": order["_id"]},
        {
            "$set": {
                "payment_status": "paid",
                "order_status": "placed",
                "razorpay_payment_id": razorpay_payment_id
            }
        }
    )

    return {"message": "Payment successful & order placed"}