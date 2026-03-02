from jose import JWTError,jwt
from datetime import datetime,timedelta
from fastapi import HTTPException,Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from database.db import user_collection

SECRET_KEY = "8763551927"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_token(data:dict,expires_delta:timedelta=None):
    to_encode = data.copy()

    expires = datetime.utcnow()+ (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp":expires})

    encode_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

async def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(security)):
    token = credentials.credentials

    try:
        paylaod= jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        email = paylaod.get("sub")  
        
        if not email:
            raise HTTPException(status_code=401,detail="invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    res =  await user_collection.find_one({"email":email})
    return res

def role_required(role:str):
    def role_check(current_user:str=Depends(get_current_user)):
        if current_user.get("role")!= role:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return role_check

        




