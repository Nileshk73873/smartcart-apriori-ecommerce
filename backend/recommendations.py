from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd
from .database import get_db
from . import models
from sqlalchemy.orm import Session
import os

router = APIRouter(prefix="/api", tags=["recommendations"])

RULES_FILE = Path(__file__).resolve().parent.parent / "outputs" / "strong_association_rules.csv"

# Global cache for rules
RULES_CACHE = None

def load_rules():
    global RULES_CACHE
    if RULES_CACHE is None:
        if RULES_FILE.exists():
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
    Given a product, find matching rules.
    Prioritizes direct antecedent matches, then complementary rules, and finally top high-lift rules.
    """
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    rules_df = load_rules()
    if rules_df.empty:
        return []

    recs = []
    seen = {product.name}

    def add_item(item_name: str, row_data: Any, reason_text: str):
        if item_name not in seen:
            seen.add(item_name)
            rec_prod = db.query(models.Product).filter(models.Product.name == item_name).first()
            if rec_prod:
                recs.append({
                    "product": {
                        "id": rec_prod.id,
                        "name": rec_prod.name,
                        "price": rec_prod.price,
                        "stock_code": rec_prod.stock_code,
                        "stockCode": rec_prod.stock_code,
                        "image": rec_prod.image_url,
                        "image_url": rec_prod.image_url
                    },
                    "support": round(float(row_data["support"]), 4),
                    "confidence": round(float(row_data["confidence"]), 4),
                    "lift": round(float(row_data["lift"]), 2),
                    "reason": reason_text
                })

    # Stage 1: Exact or subset match in antecedents
    def is_ant_match(ant_val):
        if pd.isna(ant_val):
            return False
        parts = {p.strip() for p in str(ant_val).split("+")}
        return product.name in parts

    matches_ant = rules_df[rules_df["antecedents"].apply(is_ant_match)].copy()
    if not matches_ant.empty:
        matches_ant = matches_ant.sort_values(by=["lift", "confidence"], ascending=[False, False])
        for _, row in matches_ant.iterrows():
            consequents = [c.strip() for c in str(row["consequents"]).split("+")]
            for item in consequents:
                add_item(item, row, "Frequently bought together")
                if len(recs) >= 10:
                    break
            if len(recs) >= 10:
                break

    # Stage 2: Match in consequents (recommending the complementary antecedents)
    if len(recs) < 4:
        def is_con_match(con_val):
            if pd.isna(con_val):
                return False
            parts = {p.strip() for p in str(con_val).split("+")}
            return product.name in parts

        matches_con = rules_df[rules_df["consequents"].apply(is_con_match)].copy()
        if not matches_con.empty:
            matches_con = matches_con.sort_values(by=["lift", "confidence"], ascending=[False, False])
            for _, row in matches_con.iterrows():
                antecedents = [a.strip() for a in str(row["antecedents"]).split("+")]
                for item in antecedents:
                    add_item(item, row, "Frequently bought together")
                    if len(recs) >= 10:
                        break
                if len(recs) >= 10:
                    break

    # Stage 3: Backfill with top highest-lift rules if the item is rare/unmatched
    if len(recs) < 4:
        top_rules = rules_df.sort_values(by=["lift", "confidence"], ascending=[False, False])
        for _, row in top_rules.iterrows():
            items = [a.strip() for a in str(row["antecedents"]).split("+")] + [
                c.strip() for c in str(row["consequents"]).split("+")
            ]
            for item in items:
                add_item(item, row, "Popular Trending Bundle Item")
                if len(recs) >= 6:
                    break
            if len(recs) >= 6:
                break

    return recs


@router.post("/cart/recommendations")
def get_cart_recommendations(cart_items: List[int], db: Session = Depends(get_db)):
    """
    Given a list of product IDs in cart, recommend next items.
    Recommends complementary bundle items from association rules, with fallback to top bundles.
    """
    if not cart_items:
        return []

    products = db.query(models.Product).filter(models.Product.id.in_(cart_items)).all()
    product_names = {p.name for p in products}

    rules_df = load_rules()
    if rules_df.empty:
        return []

    recs = []
    seen = set(product_names)

    def add_cart_rec(item_name: str, row_data: Any, reason_text: str):
        if item_name not in seen:
            seen.add(item_name)
            rec_prod = db.query(models.Product).filter(models.Product.name == item_name).first()
            if rec_prod:
                recs.append({
                    "product": {
                        "id": rec_prod.id,
                        "name": rec_prod.name,
                        "price": rec_prod.price,
                        "stock_code": rec_prod.stock_code,
                        "stockCode": rec_prod.stock_code,
                        "image": rec_prod.image_url,
                        "image_url": rec_prod.image_url
                    },
                    "support": round(float(row_data["support"]), 4),
                    "confidence": round(float(row_data["confidence"]), 4),
                    "lift": round(float(row_data["lift"]), 2),
                    "reason": reason_text
                })

    # Stage 1: Rules where any cart product is in the antecedent
    def has_cart_item_in_ant(ant_val):
        if pd.isna(ant_val):
            return False
        parts = {p.strip() for p in str(ant_val).split("+")}
        return bool(parts & product_names)

    matches_ant = rules_df[rules_df["antecedents"].apply(has_cart_item_in_ant)].copy()
    if not matches_ant.empty:
        matches_ant = matches_ant.sort_values(by=["lift", "confidence"], ascending=[False, False])
        for _, row in matches_ant.iterrows():
            consequents = [c.strip() for c in str(row["consequents"]).split("+")]
            for item in consequents:
                add_cart_rec(item, row, "Customers who bought items in your cart also bought this")
                if len(recs) >= 10:
                    break
            if len(recs) >= 10:
                break

    # Stage 2: Rules where any cart product is in the consequent
    if len(recs) < 6:
        def has_cart_item_in_con(con_val):
            if pd.isna(con_val):
                return False
            parts = {p.strip() for p in str(con_val).split("+")}
            return bool(parts & product_names)

        matches_con = rules_df[rules_df["consequents"].apply(has_cart_item_in_con)].copy()
        if not matches_con.empty:
            matches_con = matches_con.sort_values(by=["lift", "confidence"], ascending=[False, False])
            for _, row in matches_con.iterrows():
                antecedents = [a.strip() for a in str(row["antecedents"]).split("+")]
                for item in antecedents:
                    add_cart_rec(item, row, "Complete your bundle with this item")
                    if len(recs) >= 10:
                        break
                if len(recs) >= 10:
                    break

    # Stage 3: Fallback to top overall bundle items so cart is never empty
    if len(recs) < 4:
        top_rules = rules_df.sort_values(by=["lift", "confidence"], ascending=[False, False])
        for _, row in top_rules.iterrows():
            items = [a.strip() for a in str(row["antecedents"]).split("+")] + [
                c.strip() for c in str(row["consequents"]).split("+")
            ]
            for item in items:
                add_cart_rec(item, row, "Frequently bought together across SmartCart")
                if len(recs) >= 6:
                    break
            if len(recs) >= 6:
                break

    return recs
