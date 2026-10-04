"""
Data Preprocessing Module for Online Retail Association Mining.
Cleans raw transaction logs into valid, completed shopping baskets.
"""

from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def clean_retail_data(
    df: pd.DataFrame,
    save_output: bool = True,
    output_path: Optional[str | Path] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Clean the Online Retail II dataset according to Association Rule Mining requirements:
    1. Remove cancelled invoices (Invoice starts with 'C')
    2. Remove Quantity <= 0 (returns and inventory adjustments)
    3. Remove Price <= 0 (free items, internal adjustments, bad entries)
    4. Remove missing or blank Descriptions
    5. Clean and standardize Description text (strip whitespace, normalize spaces)
    6. Retain Customer ID without dropping missing customer rows (basket is per Invoice)
    7. Remove duplicate transaction rows

    Parameters
    ----------
    df : pd.DataFrame
        Raw dataset.
    save_output : bool, default True
        Whether to save the cleaned dataset to disk.
    output_path : str or Path, optional
        Path where cleaned CSV should be saved.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, Any]]
        Cleaned DataFrame and a dictionary of cleaning statistics.
    """
    rows_before = len(df)
    logger.info(f"Starting data preprocessing on {rows_before:,} rows...")

    # Make a copy to avoid mutating the original
    cleaned = df.copy()

    # Step 1: Remove cancelled invoices
    invoice_str = cleaned["Invoice"].astype(str).str.strip()
    is_cancelled = invoice_str.str.startswith("C", na=False)
    cleaned = cleaned[~is_cancelled].copy()
    rows_after_cancelled = len(cleaned)
    cancelled_removed = rows_before - rows_after_cancelled

    # Step 2: Remove Quantity <= 0
    cleaned = cleaned[cleaned["Quantity"] > 0].copy()
    rows_after_qty = len(cleaned)
    invalid_qty_removed = rows_after_cancelled - rows_after_qty

    # Step 3: Remove Price <= 0
    cleaned = cleaned[cleaned["Price"] > 0].copy()
    rows_after_price = len(cleaned)
    invalid_price_removed = rows_after_qty - rows_after_price

    # Step 4 & 5: Clean Description & Remove missing / blanks
    cleaned = cleaned[cleaned["Description"].notnull()].copy()
    cleaned["Description"] = (
        cleaned["Description"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )
    cleaned = cleaned[cleaned["Description"] != ""].copy()
    rows_after_desc = len(cleaned)
    invalid_desc_removed = rows_after_price - rows_after_desc

    # Step 5b: Drop non-product rows (StockCode or Description)
    non_product_codes = {
        "POST", "DOT", "M", "D", "C2", "BANK CHARGES", "AMAZONFEE",
        "CRUK", "S", "B", "ADJUST", "MANUAL", "POSTAGE",
        "DOTCOM POSTAGE", "CARRIAGE", "SAMPLES", "DISCOUNT"
    }
    stock_is_non_prod = cleaned["StockCode"].astype(str).str.strip().str.upper().isin(non_product_codes)
    desc_is_non_prod = cleaned["Description"].astype(str).str.strip().str.upper().isin(non_product_codes)
    is_non_prod = stock_is_non_prod | desc_is_non_prod
    cleaned = cleaned[~is_non_prod].copy()
    rows_after_non_prod = len(cleaned)
    non_products_removed = rows_after_desc - rows_after_non_prod

    # Step 6: Invoice formatting & Date parsing
    cleaned["Invoice"] = cleaned["Invoice"].astype(str).str.strip()
    if "InvoiceDate" in cleaned.columns:
        cleaned["InvoiceDate"] = pd.to_datetime(cleaned["InvoiceDate"], format="mixed", dayfirst=True)

    # Step 7: Calculate Total Line Amount for business reference
    cleaned["LineTotal"] = cleaned["Quantity"] * cleaned["Price"]

    # Step 8: Remove duplicate rows
    cols_to_check = [
        "Invoice", "StockCode", "Description", "Quantity",
        "InvoiceDate", "Price", "Customer ID", "Country"
    ]
    # Check only available columns
    check_cols = [c for c in cols_to_check if c in cleaned.columns]
    rows_before_dedup = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=check_cols).copy()
    duplicates_removed = rows_before_dedup - len(cleaned)

    rows_after = len(cleaned)
    total_removed = rows_before - rows_after
    pct_removed = (total_removed / rows_before) * 100.0 if rows_before > 0 else 0.0

    stats = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": total_removed,
        "percentage_removed": round(pct_removed, 2),
        "cancelled_removed": cancelled_removed,
        "invalid_qty_removed": invalid_qty_removed,
        "invalid_price_removed": invalid_price_removed,
        "invalid_desc_removed": invalid_desc_removed,
        "non_products_removed": non_products_removed,
        "duplicates_removed": duplicates_removed,
        "unique_invoices": int(cleaned["Invoice"].nunique()),
        "unique_products": int(cleaned["Description"].nunique()),
        "unique_countries": int(cleaned["Country"].nunique()),
        "date_min": str(cleaned["InvoiceDate"].min()) if "InvoiceDate" in cleaned.columns else "",
        "date_max": str(cleaned["InvoiceDate"].max()) if "InvoiceDate" in cleaned.columns else ""
    }

    logger.info(
        f"Preprocessing complete: {rows_after:,} rows retained "
        f"({total_removed:,} removed, {pct_removed:.2f}%). "
        f"Unique Invoices: {stats['unique_invoices']:,}, Products: {stats['unique_products']:,}."
    )

    if save_output:
        if output_path is None:
            output_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
            output_dir.mkdir(parents=True, exist_ok=True)
            target = output_dir / "cleaned_retail.csv"
        else:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving cleaned dataset to {target.resolve()}...")
        cleaned.to_csv(target, index=False)
        logger.info("Saved cleaned dataset successfully.")

    return cleaned, stats
