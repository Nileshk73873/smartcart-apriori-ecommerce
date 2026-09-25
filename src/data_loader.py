"""
Data Loader Module for Online Retail II Dataset.
Handles safe loading, validation, and summary reporting of raw transaction data.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country"
]


def find_default_dataset_path() -> Path:
    """
    Search for online_retail_II.csv in standard project locations.
    """
    candidates = [
        Path("data/raw/online_retail_II.csv"),
        Path("online_retail_II.csv"),
        Path("../data/raw/online_retail_II.csv"),
        Path("../online_retail_II.csv")
    ]
    for p in candidates:
        if p.is_file():
            return p
    # Default fallback
    return Path("data/raw/online_retail_II.csv")


def load_dataset(file_path: Optional[str | Path] = None, nrows: Optional[int] = None) -> pd.DataFrame:
    """
    Safely load the Online Retail II CSV dataset into a pandas DataFrame.

    Parameters
    ----------
    file_path : str or Path, optional
        Path to the CSV file. If None, default project paths will be checked.
    nrows : int, optional
        Number of rows to read (useful for quick previews or testing).

    Returns
    -------
    pd.DataFrame
        Loaded raw transaction DataFrame.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist.
    ValueError
        If required columns are missing.
    """
    if file_path is None:
        path = find_default_dataset_path()
    else:
        path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Dataset not found at '{path}'. Please ensure 'online_retail_II.csv' is placed in "
            f"'data/raw/' or the project root directory."
        )

    logger.info(f"Loading raw dataset from {path.resolve()}...")
    df = pd.read_csv(
        path,
        nrows=nrows,
        dtype={
            "Invoice": str,
            "StockCode": str,
            "Description": str,
            "Country": str
        }
    )

    # Validate columns
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Dataset at '{path}' is missing required columns: {missing_cols}. "
            f"Expected columns: {REQUIRED_COLUMNS}"
        )

    logger.info(f"Successfully loaded dataset with shape {df.shape}.")
    return df


def inspect_raw_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a comprehensive diagnostic report of the raw dataset.

    Parameters
    ----------
    df : pd.DataFrame
        The raw dataset.

    Returns
    -------
    dict
        Dictionary containing detailed summary statistics.
    """
    invoice_str = df["Invoice"].astype(str).str.strip()
    is_cancelled = invoice_str.str.startswith("C", na=False)

    summary = {
        "total_rows": int(len(df)),
        "total_columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {col: int(cnt) for col, cnt in df.isnull().sum().items()},
        "duplicate_rows": int(df.duplicated().sum()),
        "cancelled_invoice_rows": int(is_cancelled.sum()),
        "unique_invoices_total": int(df["Invoice"].nunique()),
        "unique_invoices_cancelled": int(df.loc[is_cancelled, "Invoice"].nunique()),
        "unique_stock_codes": int(df["StockCode"].nunique()),
        "unique_descriptions": int(df["Description"].dropna().nunique()),
        "unique_customers": int(df["Customer ID"].dropna().nunique()),
        "unique_countries": int(df["Country"].nunique()),
        "quantity_stats": {
            "min": int(df["Quantity"].min()),
            "max": int(df["Quantity"].max()),
            "median": float(df["Quantity"].median()),
            "mean": float(df["Quantity"].mean()),
            "zero_or_negative_count": int((df["Quantity"] <= 0).sum()),
            "negative_count": int((df["Quantity"] < 0).sum()),
            "zero_count": int((df["Quantity"] == 0).sum())
        },
        "price_stats": {
            "min": float(df["Price"].min()),
            "max": float(df["Price"].max()),
            "median": float(df["Price"].median()),
            "mean": float(df["Price"].mean()),
            "zero_or_negative_count": int((df["Price"] <= 0).sum()),
            "negative_count": int((df["Price"] < 0).sum()),
            "zero_count": int((df["Price"] == 0).sum())
        },
        "date_range": {
            "min": str(df["InvoiceDate"].min()),
            "max": str(df["InvoiceDate"].max())
        }
    }
    return summary


def print_dataset_report(summary: Dict[str, Any]) -> None:
    """Pretty print the dataset diagnostic report."""
    print("=" * 60)
    print("ONLINE RETAIL II - RAW DATASET DIAGNOSTIC REPORT")
    print("=" * 60)
    print(f"Total Rows:             {summary['total_rows']:,}")
    print(f"Total Columns:          {summary['total_columns']}")
    print(f"Unique Invoices:        {summary['unique_invoices_total']:,} (Cancelled: {summary['unique_invoices_cancelled']:,})")
    print(f"Unique Products (Desc): {summary['unique_descriptions']:,}")
    print(f"Unique Customers:       {summary['unique_customers']:,}")
    print(f"Unique Countries:       {summary['unique_countries']}")
    print(f"Date Range:             {summary['date_range']['min']} to {summary['date_range']['max']}")
    print("-" * 60)
    print("Data Quality Issues Detected in Raw File:")
    print(f" - Duplicate Rows:       {summary['duplicate_rows']:,}")
    print(f" - Cancelled Invoices:   {summary['cancelled_invoice_rows']:,} rows")
    print(f" - Quantity <= 0:        {summary['quantity_stats']['zero_or_negative_count']:,} rows")
    print(f" - Price <= 0:           {summary['price_stats']['zero_or_negative_count']:,} rows")
    print(f" - Missing Descriptions: {summary['missing_values'].get('Description', 0):,} rows")
    print(f" - Missing Customer IDs: {summary['missing_values'].get('Customer ID', 0):,} rows (Retained for baskets)")
    print("=" * 60)
