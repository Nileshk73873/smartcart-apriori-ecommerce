"""
Association Rules Module.
Extracts, evaluates, and filters association rules using Support, Confidence, and Lift.
"""

from pathlib import Path
from typing import Optional, Literal
import pandas as pd
from mlxtend.frequent_patterns import association_rules
import logging

logger = logging.getLogger(__name__)

DEFAULT_MIN_CONFIDENCE = 0.30
DEFAULT_MIN_LIFT = 1.20


def generate_rules(
    frequent_itemsets: pd.DataFrame,
    metric: str = "lift",
    min_threshold: float = 1.0,
    save_output: bool = True,
    output_path: Optional[str | Path] = None
) -> pd.DataFrame:
    """
    Generate association rules from frequent itemsets.

    Metric Explanations:
    - Support: P(A ∩ B) - How frequently the combination of antecedent and
      consequent appears among all transactions.
    - Confidence: P(B | A) = Support(A ∩ B) / Support(A) - The conditional probability
      that the consequent B is purchased given that the antecedent A is purchased.
    - Lift: Confidence(A -> B) / Support(B) = Support(A ∩ B) / (Support(A) * Support(B)) -
      The ratio of observed co-occurrence to expected co-occurrence if independent.
      Lift > 1 indicates positive association (A and B encourage each other's purchase).
      Lift = 1 indicates independence.
      Lift < 1 indicates negative association (substitutes).

    Parameters
    ----------
    frequent_itemsets : pd.DataFrame
        DataFrame of frequent itemsets from Apriori.
    metric : str, default 'lift'
        Metric to evaluate candidate rules ('lift', 'confidence', 'support').
    min_threshold : float, default 1.0
        Minimum threshold for the chosen metric.
    save_output : bool, default True
        Whether to save all generated rules to CSV.
    output_path : str or Path, optional
        Target CSV file path.

    Returns
    -------
    pd.DataFrame
        Generated association rules with metrics.
    """
    logger.info(f"Generating association rules using {metric} >= {min_threshold}...")

    # Filter itemsets to only those with length >= 2
    multi_itemsets = frequent_itemsets[frequent_itemsets["length"] >= 2]
    if multi_itemsets.empty:
        logger.warning("No itemsets of length >= 2 available. Cannot generate association rules.")
        return pd.DataFrame(
            columns=[
                "antecedents", "consequents", "antecedent support", "consequent support",
                "support", "confidence", "lift", "leverage", "conviction",
                "antecedents_str", "consequents_str", "rule_str"
            ]
        )

    rules = association_rules(
        frequent_itemsets,
        metric=metric,
        min_threshold=min_threshold
    )

    if rules.empty:
        logger.warning("No association rules found meeting initial threshold.")
        return rules

    # Human-readable string columns for display and export
    rules["antecedents_str"] = rules["antecedents"].apply(lambda s: " + ".join(sorted(list(s))))
    rules["consequents_str"] = rules["consequents"].apply(lambda s: " + ".join(sorted(list(s))))
    rules["rule_str"] = rules["antecedents_str"] + "  -->  " + rules["consequents_str"]

    # Antecedent and consequent lengths
    rules["antecedent_len"] = rules["antecedents"].apply(len)
    rules["consequent_len"] = rules["consequents"].apply(len)

    # Sort descending by lift by default
    rules = rules.sort_values(by="lift", ascending=False).reset_index(drop=True)

    logger.info(f"Generated {len(rules):,} association rules.")

    if save_output:
        if output_path is None:
            output_dir = Path("outputs")
            output_dir.mkdir(parents=True, exist_ok=True)
            target = output_dir / "association_rules.csv"
        else:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving all association rules to {target.resolve()}...")
        export_rules_to_csv(rules, target)

    return rules


def filter_strong_rules(
    rules: pd.DataFrame,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    min_lift: float = DEFAULT_MIN_LIFT,
    min_support: Optional[float] = None,
    sort_by: Literal["lift", "confidence", "support"] = "lift",
    save_output: bool = True,
    output_path: Optional[str | Path] = None
) -> pd.DataFrame:
    """
    Filter rules to isolate commercially viable, statistically strong rules.

    Parameters
    ----------
    rules : pd.DataFrame
        DataFrame of generated association rules.
    min_confidence : float, default 0.30
        Minimum confidence threshold.
    min_lift : float, default 1.20
        Minimum lift threshold (must be strictly > 1.0 for positive association).
    min_support : float, optional
        Minimum rule support threshold.
    sort_by : {'lift', 'confidence', 'support'}, default 'lift'
        Primary metric to sort the filtered rules.
    save_output : bool, default True
        Whether to save strong rules to CSV.
    output_path : str or Path, optional
        Target CSV file path.

    Returns
    -------
    pd.DataFrame
        Filtered and sorted strong association rules.
    """
    if rules.empty:
        return rules

    mask = (rules["confidence"] >= min_confidence) & (rules["lift"] >= min_lift)
    if min_support is not None:
        mask = mask & (rules["support"] >= min_support)

    strong_rules = rules[mask].copy()

    # Sort neutrally according to selected dimension
    sort_col = sort_by if sort_by in ["lift", "confidence", "support"] else "lift"
    strong_rules = strong_rules.sort_values(by=[sort_col, "lift"], ascending=[False, False]).reset_index(drop=True)

    logger.info(
        f"Filtered {len(strong_rules):,} strong rules "
        f"(confidence >= {min_confidence:.2f}, lift >= {min_lift:.2f}, sorted by {sort_col})."
    )

    if save_output:
        if output_path is None:
            output_dir = Path("outputs")
            output_dir.mkdir(parents=True, exist_ok=True)
            target = output_dir / "strong_association_rules.csv"
        else:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving strong association rules to {target.resolve()}...")
        export_rules_to_csv(strong_rules, target)

    return strong_rules


def export_rules_to_csv(rules_df: pd.DataFrame, target_path: Path) -> None:
    """Helper function to export clean formatted rules to CSV."""
    if rules_df.empty:
        rules_df.to_csv(target_path, index=False)
        return

    cols_to_export = [
        "antecedents_str", "consequents_str", "rule_str",
        "support", "confidence", "lift",
        "antecedent support", "consequent support",
        "leverage", "conviction"
    ]
    export_cols = [c for c in cols_to_export if c in rules_df.columns]
    export_df = rules_df[export_cols].rename(columns={
        "antecedents_str": "antecedents",
        "consequents_str": "consequents",
        "rule_str": "rule"
    })
    export_df.to_csv(target_path, index=False)
