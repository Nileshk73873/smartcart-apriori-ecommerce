from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import products, recommendations, cart

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartCart API")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For prototype
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(recommendations.router)
app.include_router(cart.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to SmartCart API"}
