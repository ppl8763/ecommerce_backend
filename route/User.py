from fastapi import APIRouter,HTTPException,Depends
from schemas.Userschema import Usersignup,Userlogin
from database.db import user_collection
from utils.hash import pwd_context
from datetime import datetime
from middleware.auth import create_token,role_required
router = APIRouter()

@router.post("/signup")
async def signup(user: Usersignup):

    existing = await user_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)

    user_dict = user.dict()
    user_dict["password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()

    result = await user_collection.insert_one(user_dict)

    return {
        "id": str(result.inserted_id),
        "name": user.name,
        "email": user.email,
        "role": user.role
    }
from fastapi import HTTPException, status

@router.post("/login")
async def login(data: Userlogin):
    res = await user_collection.find_one({"email": data.email})
    
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    verify = pwd_context.verify(data.password, res["password"])
    if not verify:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong password"
        )

    token = create_token(
        data={
            "sub": res["email"],
            "role": res["role"]
        }
    )

    return {
        "message": "Login Successfully",
        "access_token": token,
        "role": res["role"],
        "email": res["email"]
    }
    
@router.get("/admin")
def getting(cur_user:dict=Depends(role_required("admin"))):
    return {"message":"hello admin",
            "email":cur_user["email"]
            }

@router.get("/user/{email}")
async def users(email:str,cur_user:dict=Depends(role_required("user"))):
    res =await user_collection.find_one({"email":email})
    res
    return {"message":"hello user",
            "email":cur_user["email"],
            "phone":cur_user["phone"]
            }

