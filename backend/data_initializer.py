import os
import sys
import pandas as pd
from sqlalchemy.orm import Session
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

    csv_path = os.path.join("data", "processed", "cleaned_retail.csv")
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}. Please run the offline Apriori pipeline first.")
        db.close()
        return
        
    print("Loading unique products from CSV...")
    df = pd.read_csv(csv_path)
    
    # Extract unique products
    # Get the latest price for each product
    latest_products = df.sort_values("InvoiceDate").groupby("StockCode").last().reset_index()
    
    print(f"Found {len(latest_products)} unique products. Inserting into SQLite...")
    
    products_to_insert = []
    
        import urllib.parse
        for _, row in latest_products.iterrows():
            name = str(row["Description"])
            # Use the first 3 words of the product name for a clean placeholder image
            short_name = '+'.join(name.split(' ')[:3])
            keyword = urllib.parse.quote(short_name)
            
            products_to_insert.append(
                Product(
                    stock_code=str(row["StockCode"]),
                    name=name,
                    price=float(row["Price"]),
                    description=f"Authentic {name} from the UK.",
                    image_url=f"https://placehold.co/400x400/f3f4f6/111827?text={keyword}"
                )
            )
        
    # Bulk save
    db.bulk_save_objects(products_to_insert)
    db.commit()
    db.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
