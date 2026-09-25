"""
Unit tests for recommendations, bundling, and discount logic.
"""

import pandas as pd
import pytest
from src.discount import calculate_bundle_discount
from src.recommendations import recommend_products, generate_bundle_recommendations


@pytest.fixture
def sample_rules_df():
    return pd.DataFrame({
        "antecedents": [frozenset(["TEA CUP"]), frozenset(["TEA CUP", "SAUCER"]), frozenset(["SUGAR BOWL"])],
        "consequents": [frozenset(["SAUCER"]), frozenset(["TEAPOT"]), frozenset(["MILK JUG"])],
        "antecedents_str": ["TEA CUP", "SAUCER + TEA CUP", "SUGAR BOWL"],
        "consequents_str": ["SAUCER", "TEAPOT", "MILK JUG"],
        "rule_str": ["TEA CUP  -->  SAUCER", "SAUCER + TEA CUP  -->  TEAPOT", "SUGAR BOWL  -->  MILK JUG"],
        "support": [0.05, 0.03, 0.02],
        "confidence": [0.75, 0.55, 0.35],
        "lift": [2.5, 1.8, 1.3]
    })


def test_discount_business_rules():
    # Very Strong: Conf >= 0.70, Lift >= 2.0 -> 5%
    d1 = calculate_bundle_discount(confidence=0.75, lift=2.5)
    assert d1["discount_pct"] == 5.0
    assert d1["tier"] == "Very Strong Relationship"

    # Strong: Conf >= 0.50, Lift >= 1.5 -> 10%
    d2 = calculate_bundle_discount(confidence=0.55, lift=1.8)
    assert d2["discount_pct"] == 10.0
    assert d2["tier"] == "Strong Relationship"

    # Moderate: Conf >= 0.30, Lift >= 1.2 -> 15%
    d3 = calculate_bundle_discount(confidence=0.35, lift=1.3)
    assert d3["discount_pct"] == 15.0
    assert d3["tier"] == "Moderate Relationship"

    # Below threshold -> 0%
    d4 = calculate_bundle_discount(confidence=0.20, lift=1.1)
    assert d4["discount_pct"] == 0.0
    assert "No Discount" in d4["tier"]


def test_recommend_products_success(sample_rules_df):
    res = recommend_products("TEA CUP", sample_rules_df, sort_by="lift")
    assert res["status"] == "success"
    assert len(res["recommendations"]) >= 1
    top_rec = res["recommendations"][0]
    assert top_rec["target_product"] == "TEA CUP"
    assert top_rec["recommended_product"] in ["SAUCER", "TEAPOT"]
    assert top_rec["suggested_discount_pct"] in [5.0, 10.0]


def test_recommend_products_unknown_item(sample_rules_df):
    res = recommend_products("NONEXISTENT PRODUCT XYZ", sample_rules_df)
    assert res["status"] == "no_rules_found"
    assert len(res["recommendations"]) == 0


def test_bundle_generation_preserves_multi_items(sample_rules_df):
    bundles = generate_bundle_recommendations(sample_rules_df, min_confidence=0.3, min_lift=1.2, save_output=False)
    assert not bundles.empty
    # Rule 2 has TEA CUP + SAUCER -> TEAPOT; full bundle must have 3 items
    bundle_3_items = bundles[bundles["bundle_size"] == 3]
    assert len(bundle_3_items) == 1
    items_in_bundle = bundle_3_items.iloc[0]["bundle_name"].split(" + ")
    assert set(items_in_bundle) == {"TEA CUP", "SAUCER", "TEAPOT"}
