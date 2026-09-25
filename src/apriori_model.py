"""
Apriori Model Module.
Runs the Apriori algorithm on binary basket matrices to discover frequent itemsets.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
from mlxtend.frequent_patterns import apriori
import logging

logger = logging.getLogger(__name__)

DEFAULT_MIN_SUPPORT = 0.01


def run_apriori(
    basket_df: pd.DataFrame,
    min_support: float = DEFAULT_MIN_SUPPORT,
    max_len: Optional[int] = None,
    save_output: bool = True,
    output_path: Optional[str | Path] = None
) -> pd.DataFrame:
    """
    Run the Apriori algorithm to find frequent itemsets.

    Parameters
    ----------
    basket_df : pd.DataFrame
        Binary transaction matrix (Invoices x Products).
    min_support : float, default 0.01
        Minimum support threshold (0.01 = 1% of transactions).
    max_len : int, optional
        Maximum length of itemsets to evaluate.
    save_output : bool, default True
        Whether to save results to CSV.
    output_path : str or Path, optional
        Destination path for frequent itemsets CSV.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['support', 'itemsets', 'length'],
        sorted by support descending.
    """
    logger.info(
        f"Running Apriori algorithm with min_support={min_support:.4f} "
        f"({min_support * 100:.2f}% of transactions)..."
    )

    if basket_df.empty:
        raise ValueError("Basket matrix is empty. Cannot run Apriori.")

    # Optimization: Filter out columns with column support < min_support
    # Anti-monotonicity property guarantees these items cannot form frequent itemsets.
    col_supports = basket_df.mean(axis=0)
    valid_cols = col_supports[col_supports >= min_support].index
    logger.info(
        f"Columns with individual support >= {min_support}: "
        f"{len(valid_cols):,} out of {basket_df.shape[1]:,} products."
    )

    if len(valid_cols) == 0:
        logger.warning(f"No products satisfy min_support >= {min_support}. Try lowering min_support.")
        empty_df = pd.DataFrame(columns=["support", "itemsets", "length"])
        return empty_df

    filtered_basket = basket_df[valid_cols]

    # Run mlxtend apriori
    frequent_itemsets = apriori(
        filtered_basket,
        min_support=min_support,
        use_colnames=True,
        max_len=max_len,
        low_memory=True
    )

    if frequent_itemsets.empty:
        logger.warning("No frequent itemsets found with the specified min_support threshold.")
        frequent_itemsets["length"] = 0
        return frequent_itemsets

    # Add itemset length
    frequent_itemsets["length"] = frequent_itemsets["itemsets"].apply(len)

    # Sort descending by support
    frequent_itemsets = frequent_itemsets.sort_values(by=["support", "length"], ascending=[False, False]).reset_index(drop=True)

    logger.info(
        f"Apriori completed: Found {len(frequent_itemsets):,} frequent itemsets. "
        f"Length breakdown:\n{frequent_itemsets['length'].value_counts().to_dict()}"
    )

    if save_output:
        if output_path is None:
            output_dir = Path("outputs")
            output_dir.mkdir(parents=True, exist_ok=True)
            target = output_dir / "frequent_itemsets.csv"
        else:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving frequent itemsets to {target.resolve()}...")
        # Convert frozenset to readable string for CSV
        csv_df = frequent_itemsets.copy()
        csv_df["itemsets"] = csv_df["itemsets"].apply(lambda s: " + ".join(sorted(list(s))))
        csv_df.to_csv(target, index=False)
        logger.info("Saved frequent itemsets CSV.")

    return frequent_itemsets
