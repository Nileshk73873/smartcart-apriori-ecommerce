import os
import sys
import urllib.parse
from pathlib import Path

import pandas as pd
from backend.database import SessionLocal, engine, Base
from backend.models import Product


def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Check if products already exist
    if db.query(Product).first():
        print("Products already exist in DB. Skipping init.")
        db.close()
        return

    csv_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "cleaned_retail.csv"

    if not csv_path.exists():
        print(
            f"Error: Could not find {csv_path}. "
            "Please run the offline Apriori pipeline first."
        )
        db.close()
        return

    print("Loading unique products from CSV...")
    df = pd.read_csv(csv_path)

    # Extract unique products
    # Parse InvoiceDate and get the latest price for each product description
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="mixed")
    latest_products = (
        df.sort_values("InvoiceDate")
        .groupby("Description")
        .last()
        .reset_index()
    )

    print(
        f"Found {len(latest_products)} unique products. "
        "Inserting into SQLite..."
    )

    products_to_insert = []

    for _, row in latest_products.iterrows():
        name = str(row["Description"])

        # Use the first 3 words of the product name for a clean placeholder image
        short_name = "+".join(name.split(" ")[:3])
        keyword = urllib.parse.quote(short_name)

        products_to_insert.append(
            Product(
                stock_code=str(row["StockCode"]),
                name=name,
                price=float(row["Price"]),
                description=f"Authentic {name} from the UK.",
                image_url=(
                    "https://placehold.co/400x400/f3f4f6/111827"
                    f"?text={keyword}"
                ),
            )
        )

    # Bulk save
    db.bulk_save_objects(products_to_insert)
    db.commit()
    db.close()

    print("Database initialization complete.")


if __name__ == "__main__":
    init_db()
