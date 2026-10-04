"""
Product Recommendation and Bundle Generation Module.
Provides interactive product cross-sell recommendations and generates
multi-item bundles with business-rule discount recommendations.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Literal
import pandas as pd
from src.discount import calculate_bundle_discount
import logging

logger = logging.getLogger(__name__)


def find_matching_products(query: str, all_products: List[str], limit: int = 10) -> List[str]:
    """
    Find matching products in the catalog using case-insensitive substring search.

    Parameters
    ----------
    query : str
        Search term.
    all_products : list of str
        List of all unique product names in the catalog.
    limit : int, default 10
        Maximum number of matched suggestions to return.

    Returns
    -------
    list of str
        Matching product names.
    """
    clean_query = query.strip().upper()
    if not clean_query:
        return []

    # Exact match first
    exact = [p for p in all_products if p.upper() == clean_query]
    if exact:
        return exact

    # Substring match
    matches = [p for p in all_products if clean_query in p.upper()]
    return matches[:limit]


def recommend_products(
    product_name: str,
    rules_df: pd.DataFrame,
    sort_by: Literal["lift", "confidence", "support"] = "lift",
    top_n: int = 5
) -> Dict[str, Any]:
    """
    Recommend complementary products when a customer views or selects a product.

    Searches association rules where the target product appears in the antecedent set.

    Parameters
    ----------
    product_name : str
        Name of the product selected by the user.
    rules_df : pd.DataFrame
        DataFrame of association rules.
    sort_by : {'lift', 'confidence', 'support'}, default 'lift'
        Primary sorting metric for ranked recommendations.
    top_n : int, default 5
        Number of top recommendations to return.

    Returns
    -------
    dict
        Dictionary containing status, matched product name, recommendations list,
        and diagnostic message.
    """
    if rules_df.empty:
        return {
            "status": "empty_rules",
            "product_name": product_name,
            "recommendations": [],
            "message": "No association rules have been generated yet."
        }

    clean_name = product_name.strip()

    # Match rules where antecedent is a subset of the viewed product (exact match for single product)
    def is_exact_antecedent(antecedent_val) -> bool:
        if isinstance(antecedent_val, (set, frozenset)):
            items = {str(item).strip() for item in antecedent_val}
            return items == {clean_name}
        if isinstance(antecedent_val, str):
            parts = {p.strip() for p in antecedent_val.split("+")}
            return parts == {clean_name}
        return False

    matching_rules = rules_df[rules_df["antecedents"].apply(is_exact_antecedent)].copy()

    if matching_rules.empty:
        return {
            "status": "no_rules_found",
            "product_name": product_name,
            "recommendations": [],
            "message": (
                f"No association rules found where '{product_name}' appears as an antecedent. "
                f"Try lowering the minimum support or confidence thresholds."
            )
        }

    # Sort matching rules
    sort_col = sort_by if sort_by in ["lift", "confidence", "support"] else "lift"
    matching_rules = matching_rules.sort_values(by=[sort_col, "lift"], ascending=[False, False])

    recommendations = []
    seen_consequents = set()

    for _, row in matching_rules.iterrows():
        consequent_str = (
            row["consequents_str"]
            if "consequents_str" in row
            else " + ".join(sorted(list(row["consequents"])))
        )

        # Avoid redundant duplicate consequent suggestions
        if consequent_str in seen_consequents:
            continue
        seen_consequents.add(consequent_str)

        antecedent_str = (
            row["antecedents_str"]
            if "antecedents_str" in row
            else " + ".join(sorted(list(row["antecedents"])))
        )

        conf = float(row["confidence"])
        lift_val = float(row["lift"])
        sup = float(row["support"])

        # Discount business rule
        discount_info = calculate_bundle_discount(confidence=conf, lift=lift_val)

        # Form full bundle
        bundle_items = list(dict.fromkeys(
            [item.strip() for item in antecedent_str.split("+")] +
            [item.strip() for item in consequent_str.split("+")]
        ))
        bundle_str = " + ".join(bundle_items)

        recommendations.append({
            "target_product": clean_name,
            "recommended_product": consequent_str,
            "bundle": bundle_str,
            "bundle_items": bundle_items,
            "support": round(sup, 4),
            "confidence": round(conf, 4),
            "lift": round(lift_val, 2),
            "suggested_discount_pct": discount_info["discount_pct"],
            "discount_tier": discount_info["tier"],
            "discount_rationale": discount_info["rationale"],
            "rule_text": f"{antecedent_str}  -->  {consequent_str}"
        })

        if len(recommendations) >= top_n:
            break

    return {
        "status": "success",
        "product_name": clean_name,
        "recommendations": recommendations,
        "count": len(recommendations),
        "message": f"Found {len(recommendations)} recommendations for '{clean_name}'."
    }


def generate_bundle_recommendations(
    rules_df: pd.DataFrame,
    min_confidence: float = 0.30,
    min_lift: float = 1.20,
    save_output: bool = True,
    output_path: Optional[str | Path] = None
) -> pd.DataFrame:
    """
    Generate complete catalog product bundles from strong association rules.

    Parameters
    ----------
    rules_df : pd.DataFrame
        Association rules dataframe.
    min_confidence : float, default 0.30
        Minimum rule confidence.
    min_lift : float, default 1.20
        Minimum rule lift.
    save_output : bool, default True
        Whether to export to CSV.
    output_path : str or Path, optional
        Target CSV file path.

    Returns
    -------
    pd.DataFrame
        DataFrame of product bundles with support, confidence, lift, and suggested discounts.
    """
    logger.info("Generating product bundle recommendations...")

    if rules_df.empty:
        return pd.DataFrame()

    # Filter by confidence and lift
    valid = rules_df[
        (rules_df["confidence"] >= min_confidence) &
        (rules_df["lift"] >= min_lift)
    ].copy()

    if valid.empty:
        logger.warning("No rules passed thresholds for bundling.")
        return pd.DataFrame()

    bundles = []
    seen_itemsets = set()

    for _, row in valid.iterrows():
        # Get raw item sets
        ant = (
            set(row["antecedents"])
            if isinstance(row["antecedents"], (set, frozenset))
            else set(str(row["antecedents"]).split(" + "))
        )
        con = (
            set(row["consequents"])
            if isinstance(row["consequents"], (set, frozenset))
            else set(str(row["consequents"]).split(" + "))
        )

        full_set = frozenset(ant.union(con))
        # Unique canonical bundle representation
        bundle_key = tuple(sorted(list(full_set)))

        conf = float(row["confidence"])
        lift_val = float(row["lift"])
        sup = float(row["support"])

        # Discount
        disc = calculate_bundle_discount(confidence=conf, lift=lift_val)

        ant_str = " + ".join(sorted(list(ant)))
        con_str = " + ".join(sorted(list(con)))
        bundle_name = " + ".join(sorted(list(full_set)))

        bundles.append({
            "bundle_key": str(bundle_key),
            "bundle_name": bundle_name,
            "bundle_size": len(full_set),
            "primary_item(s)": ant_str,
            "complementary_item(s)": con_str,
            "support": round(sup, 4),
            "confidence": round(conf, 4),
            "lift": round(lift_val, 2),
            "suggested_discount_pct": disc["discount_pct"],
            "discount_tier": disc["tier"],
            "business_rationale": disc["rationale"]
        })

    bundles_df = pd.DataFrame(bundles)

    # If multiple rules produce the identical bundle, keep the one with highest lift
    bundles_df = (
        bundles_df.sort_values(by=["lift", "confidence"], ascending=[False, False])
        .drop_duplicates(subset=["bundle_key"])
        .drop(columns=["bundle_key"])
        .reset_index(drop=True)
    )

    logger.info(f"Generated {len(bundles_df):,} unique product bundle recommendations.")

    if save_output:
        if output_path is None:
            output_dir = Path(__file__).resolve().parent.parent / "outputs"
            output_dir.mkdir(parents=True, exist_ok=True)
            target = output_dir / "bundle_recommendations.csv"
        else:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving bundle recommendations to {target.resolve()}...")
        bundles_df.to_csv(target, index=False)
        logger.info("Saved bundle recommendations CSV.")

    return bundles_df
