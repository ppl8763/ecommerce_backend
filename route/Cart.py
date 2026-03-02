from fastapi import APIRouter,Depends,HTTPException
from schemas.CartSchema import AddToCart,CartItem
from middleware.auth import get_current_user,role_required
from database.db import cart_collection,product_collection
from datetime import datetime
from bson import ObjectId
router = APIRouter()

@router.post("/add_items")
async def add_items(data:AddToCart,user_email=Depends(get_current_user)):
   
    user_id = str(user_email["_id"])
    
    product = await product_collection.find_one({"_id":ObjectId(data.product_id)})

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product["stock"]<=data.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")
    
    cart = await cart_collection.find_one({"user_id":user_id})

    if not cart:
        new_cart= {
            "user_id":user_id,
            "items":[
                {
                    "product_id":ObjectId(data.product_id),
                    "quantity":data.quantity,
                    "price_at_time":product["price"],
                    "name":product["name"],
                    "images":product["images"]
                }
            ],
            "total_ammount":product["price"]*data.quantity,
            "created_at":datetime.utcnow(),
            "updated_at":datetime.utcnow()
        }
        await cart_collection.insert_one(new_cart)
        return {"message":"Add Sucessfully"}
    update = False
    total = 0

    for item in cart["items"]:
        if item["product_id"] == ObjectId(data.product_id):
            item["quantity"]+=data.quantity
            update =True

    if not update:
        cart["items"].append({
            "product_id":ObjectId(data.product_id),
            "quantity":data.quantity,
            "price_at_time":product["price"],
            "name":product["name"],
            "images":product["images"],
        })
    for item in cart["items"]:
        total += item["quantity"]*item["price_at_time"]
    
    await cart_collection.update_one({"_id":ObjectId(cart["_id"])},
                                     {"$set":{
                                         "items":cart["items"],
                                         "total_ammount":total,
                                         "updated_at":datetime.utcnow()
                                     }}
                                     )
    return {"message": "Cart updated successfully"}
    
@router.get("/my_cart")
async def get_cart(user_email = Depends(get_current_user)):

    
    user_id = str(user_email["_id"])

    cart = await cart_collection.find_one({"user_id": user_id})

    if not cart:
        return {"message": "Cart is empty"}

    cart["_id"] = str(cart["_id"])
    cart["user_id"] = str(cart["user_id"])

    for item in cart["items"]:
        item["product_id"] = str(item["product_id"])

    return cart
@router.get("/cart")
async def count(user=Depends(get_current_user)):
    user_id = str(user["_id"])

    cart = await cart_collection.find_one({"user_id": user_id})

    if not cart:
        return {"total_items": 0}

    total_items = sum(item["quantity"] for item in cart["items"])

    return {
        "total_items": total_items
    }
@router.put("/cart/update")
async def update_quantity(data: AddToCart, user=Depends(get_current_user)):
    user_id = str(user["_id"])

    cart = await cart_collection.find_one({"user_id": user_id})

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    updated = False

    for item in cart["items"]:
        if item["product_id"] == ObjectId(data.product_id):
            item["quantity"] = data.quantity
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Product not in cart")

    # Recalculate total
    total = sum(item["quantity"] * item["price_at_time"] for item in cart["items"])

    await cart_collection.update_one(
        {"_id": cart["_id"]},
        {
            "$set": {
                "items": cart["items"],
                "total_ammount": total,
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Quantity updated successfully"}
@router.delete("/cart/delete/{product_id}")
async def delete_item(product_id: str, user=Depends(get_current_user)):
    user_id = str(user["_id"])

    cart = await cart_collection.find_one({"user_id": user_id})

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    new_items = [
        item for item in cart["items"]
        if item["product_id"] != ObjectId(product_id)
    ]

    total = sum(item["quantity"] * item["price_at_time"] for item in new_items)

    await cart_collection.update_one(
        {"_id": cart["_id"]},
        {
            "$set": {
                "items": new_items,
                "total_ammount": total,
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Item removed successfully"}