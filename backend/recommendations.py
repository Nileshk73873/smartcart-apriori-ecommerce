from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import pandas as pd
from .database import get_db
from . import models
from sqlalchemy.orm import Session
import os

router = APIRouter(prefix="/api", tags=["recommendations"])

RULES_FILE = os.path.join("outputs", "strong_association_rules.csv")

# Global cache for rules
RULES_CACHE = None

def load_rules():
    global RULES_CACHE
    if RULES_CACHE is None:
        if os.path.exists(RULES_FILE):
            RULES_CACHE = pd.read_csv(RULES_FILE)
        else:
            RULES_CACHE = pd.DataFrame()
    return RULES_CACHE

@router.get("/recommendations/related_products")
def get_related_products(db: Session = Depends(get_db)):
    rules_df = load_rules()
    if rules_df.empty:
        return []
    
    # Get unique product names from both antecedents and consequents
    product_names = set()
    for _, row in rules_df.iterrows():
        ant = [c.strip() for c in str(row["antecedents"]).split("+")]
        con = [c.strip() for c in str(row["consequents"]).split("+")]
        product_names.update(ant)
        product_names.update(con)
    
    # Fetch these products from the DB
    products = db.query(models.Product).filter(models.Product.name.in_(product_names)).all()
    return [{"id": p.id, "name": p.name} for p in products]


@router.get("/recommendations/{product_id}")
def get_product_recommendations(product_id: int, db: Session = Depends(get_db)):
    """
    Given a product, find matching rules where this product is in the antecedent.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    rules_df = load_rules()
    if rules_df.empty:
        return []

    # Search both antecedents and consequents for the product
    mask_ant = rules_df["antecedents"].str.contains(product.name, na=False, regex=False)
    mask_con = rules_df["consequents"].str.contains(product.name, na=False, regex=False)
    matches = rules_df[mask_ant | mask_con]
    
    # Sort by a combination score or lift
    # Score = 0.5 * normalized_lift + 0.3 * confidence + 0.2 * support
    # For simplicity, we just sort by lift
    matches = matches.sort_values(by="lift", ascending=False)
    
    recs = []
    seen = set()
    for _, row in matches.iterrows():
        # Get all items in this rule
        rule_items = [c.strip() for c in row["antecedents"].split("+")] + [c.strip() for c in row["consequents"].split("+")]
        for item in rule_items:
            if item not in seen and item != product.name:
                seen.add(item)
                
                # Fetch product from DB
                rec_prod = db.query(models.Product).filter(models.Product.name == item).first()
                if rec_prod:
                    recs.append({
                        "product": {
                            "id": rec_prod.id,
                            "name": rec_prod.name,
                            "price": rec_prod.price,
                            "stockCode": rec_prod.stock_code,
                            "image": rec_prod.image_url
                        },
                        "support": round(row["support"], 4),
                        "confidence": round(row["confidence"], 4),
                        "lift": round(row["lift"], 2),
                        "reason": "Frequently bought together"
                    })
        if len(recs) >= 10:
            break
            
    return recs

@router.post("/cart/recommendations")
def get_cart_recommendations(cart_items: List[int], db: Session = Depends(get_db)):
    """
    Given a list of product IDs in cart, recommend next items.
    """
    if not cart_items:
        return []
        
    products = db.query(models.Product).filter(models.Product.id.in_(cart_items)).all()
    product_names = [p.name for p in products]
    
    rules_df = load_rules()
    if rules_df.empty:
        return []
        
    # We look for rules where ALL items in the antecedent are in the cart
    # OR at least some items in the antecedent are in the cart
    # Let's find rules where antecedent is a subset of cart items
    
    def has_overlap(rule_str):
        parts = [p.strip() for p in str(rule_str).split("+")]
        return any(p in product_names for p in parts)
        
    mask_ant = rules_df["antecedents"].apply(has_overlap)
    mask_con = rules_df["consequents"].apply(has_overlap)
    matches = rules_df[mask_ant | mask_con]
    matches = matches.sort_values(by=["lift", "confidence"], ascending=False)
    
    recs = []
    seen = set(product_names)
    
    for _, row in matches.iterrows():
        rule_items = [c.strip() for c in row["antecedents"].split("+")] + [c.strip() for c in row["consequents"].split("+")]
        for item in rule_items:
            if item not in seen:
                seen.add(item)
                rec_prod = db.query(models.Product).filter(models.Product.name == item).first()
                if rec_prod:
                    recs.append({
                        "product": {
                            "id": rec_prod.id,
                            "name": rec_prod.name,
                            "price": rec_prod.price,
                            "stockCode": rec_prod.stock_code,
                            "image": rec_prod.image_url
                        },
                        "support": round(row["support"], 4),
                        "confidence": round(row["confidence"], 4),
                        "lift": round(row["lift"], 2),
                        "reason": "Customers who bought items in your cart also bought this"
                    })
        if len(recs) >= 10:
            break
            
    return recs
