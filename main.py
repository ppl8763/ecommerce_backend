from fastapi import FastAPI
from route.User import router as user
from route.Product import router as product
from route.Cart import router as cart
from route.Checkout import router as Checkout
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(user)
app.include_router(product)
app.include_router(cart)
app.include_router(Checkout)

@app.get("/")
def getting():
    return {"message": "hello"}