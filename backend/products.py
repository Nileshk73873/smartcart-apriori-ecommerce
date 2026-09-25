from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import get_db

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/", response_model=List[schemas.Product])
def get_products(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@router.get("/search", response_model=List[schemas.Product])
def search_products(q: str = Query(..., min_length=1), skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(
        models.Product.name.ilike(f"%{q}%")
    ).offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
