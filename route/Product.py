from fastapi import APIRouter,Depends,HTTPException
from database.db import product_collection
from schemas.Product import ProductCreate,ProductUpdate
from middleware.auth import role_required
from datetime import datetime
from bson import ObjectId
from fastapi import File, UploadFile
from utils.imagekit_config import imagekit
import base64
router = APIRouter()

@router.get("/all_products")
async def get_products():
    products = []
    async for product in product_collection.find():
        product["_id"] = str(product["_id"])
        products.append(product)
    return products
@router.post("/add_product")
async def add_product(
    data: ProductCreate = Depends(ProductCreate.as_form),
    file: UploadFile = File(...),
    curr: str = Depends(role_required("admin"))
):

    file_content = await file.read()
    encoded_image = base64.b64encode(file_content).decode()

    upload = imagekit.upload_file(
        file=encoded_image,
        file_name=file.filename
    )

    image_url = upload.response_metadata.raw["url"]

    product = data.dict()
    product["ratings"] = 0
    product["num_reviews"] = 0
    product["is_active"] = True
    product["created_at"] = datetime.utcnow()
    product["updated_at"] = None
    product["images"] = image_url

    result = await product_collection.insert_one(product)

    return {
        "message": "Product added successfully",
        "product_id": str(result.inserted_id),
        "image_url": image_url
    }
@router.put("/update_product/{product_id}")
async def update_product(
    product_id: str,
    data: ProductUpdate = Depends(ProductUpdate.as_form),
    file: UploadFile = File(None),
    curr: str = Depends(role_required("admin"))
    ):
    try:
        obj_id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid Product ID")

    update_data = data.dict(exclude_unset=True)

   
    if file:
        file_content = await file.read()
        encoded_image = base64.b64encode(file_content).decode()

        upload = imagekit.upload_file(
            file=encoded_image,
            file_name=file.filename
        )

        image_url = upload.response_metadata.raw["url"]
        update_data["images"] = image_url

    update_data["updated_at"] = datetime.utcnow()

    res = await product_collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )

    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product updated successfully"}

@router.delete("/delete_product/{product_id}")
async def delete_product(product_id:str,cur:str=Depends(role_required("admin"))):
    res = await product_collection.delete_one({"_id":ObjectId(product_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message":"Delete SucessFully"}
@router.get("/category_data/{category}")
async def category(category:str):
    res = await product_collection.find({"category":category}).to_list(length=None)
    for item in res:
        item["_id"] = str(item["_id"])

    return res
from bson import ObjectId
from fastapi import HTTPException

@router.get("/product/{product_id}")
async def get_single_product(product_id: str):
    try:
        obj_id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid Product ID")

    res = await product_collection.find_one({"_id": obj_id})

    if not res:
        raise HTTPException(status_code=404, detail="Product not found")

    res["_id"] = str(res["_id"])

    return res
