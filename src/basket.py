"""
Basket Transformation and Analysis Module.
Transforms cleaned transaction logs into binary shopping baskets (Invoice x Description)
and calculates descriptive basket metrics.
"""

from typing import Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
import logging

logger = logging.getLogger(__name__)


def create_basket_matrix(
    df: pd.DataFrame,
    min_item_frequency: Optional[int] = None,
    as_bool: bool = True
) -> pd.DataFrame:
    """
    Transform transaction records into an Invoice-by-Product binary basket matrix.

    Vectorized implementation using pd.factorize and scipy.sparse.csr_matrix
    for maximum speed and minimal memory footprint.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned transaction dataframe with 'Invoice' and 'Description' columns.
    min_item_frequency : int, optional
        If specified, filter out products that appear in fewer than this number
        of unique invoices. By Apriori's anti-monotonicity property, items appearing
        less than min_support * total_invoices cannot form frequent itemsets.
    as_bool : bool, default True
        If True, returns boolean values (True/False); if False, returns 0 and 1.
        mlxtend natively accepts boolean DataFrames.

    Returns
    -------
    pd.DataFrame
        Binary matrix with Invoices as rows and Descriptions as columns.
    """
    logger.info("Building binary transaction basket matrix...")

    # Extract distinct (Invoice, Description) pairs
    pairs = df[["Invoice", "Description"]].drop_duplicates()

    if min_item_frequency is not None and min_item_frequency > 1:
        item_counts = pairs["Description"].value_counts()
        frequent_items = set(item_counts[item_counts >= min_item_frequency].index)
        logger.info(
            f"Pre-filtering items: keeping {len(frequent_items):,} out of "
            f"{len(item_counts):,} items appearing in >= {min_item_frequency} invoices."
        )
        pairs = pairs[pairs["Description"].isin(frequent_items)]

    # Factorize Invoices and Descriptions into integer codes
    inv_codes, inv_labels = pd.factorize(pairs["Invoice"], sort=True)
    desc_codes, desc_labels = pd.factorize(pairs["Description"], sort=True)

    n_invoices = len(inv_labels)
    n_products = len(desc_labels)

    # Construct sparse CSR matrix (Invoice x Description)
    data = np.ones(len(pairs), dtype=bool)
    sparse_basket = csr_matrix((data, (inv_codes, desc_codes)), shape=(n_invoices, n_products))

    # Convert to dense DataFrame
    dense_array = sparse_basket.toarray()
    if not as_bool:
        dense_array = dense_array.astype(np.uint8)

    basket_df = pd.DataFrame(
        dense_array,
        index=inv_labels,
        columns=desc_labels
    )
    basket_df.index.name = "Invoice"

    mem_mb = basket_df.memory_usage().sum() / (1024 * 1024)
    logger.info(
        f"Basket matrix created: {n_invoices:,} transactions x {n_products:,} products "
        f"({mem_mb:.2f} MB)."
    )
    return basket_df


def analyze_baskets(
    df: pd.DataFrame,
    basket_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Compute descriptive statistics on shopping baskets and product frequencies.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned transaction DataFrame.
    basket_df : pd.DataFrame, optional
        Pre-built basket matrix. If None, derived directly from df.

    Returns
    -------
    dict
        Dictionary containing transaction counts, products per basket metrics,
        top 20 frequent products, and basket size distribution.
    """
    logger.info("Computing basket descriptive metrics...")

    # Unique items per invoice
    invoice_items = df.groupby("Invoice")["Description"].nunique()
    total_invoices = int(df["Invoice"].nunique())
    total_products = int(df["Description"].nunique())

    # Top products by invoice frequency
    top_products_series = (
        df.groupby("Description")["Invoice"]
        .nunique()
        .sort_values(ascending=False)
    )

    top_20_df = pd.DataFrame({
        "Description": top_products_series.head(20).index,
        "Transaction_Count": top_products_series.head(20).values,
        "Support": (top_products_series.head(20).values / total_invoices).round(4)
    })

    # Basket size statistics
    basket_stats = {
        "total_transactions": total_invoices,
        "total_unique_products": total_products,
        "avg_products_per_basket": round(float(invoice_items.mean()), 2),
        "median_products_per_basket": float(invoice_items.median()),
        "min_products_per_basket": int(invoice_items.min()),
        "max_products_per_basket": int(invoice_items.max()),
        "std_products_per_basket": round(float(invoice_items.std()), 2),
        "top_20_products": top_20_df,
        "basket_size_distribution": invoice_items.value_counts().sort_index(),
        "invoice_basket_sizes": invoice_items
    }

    return basket_stats
