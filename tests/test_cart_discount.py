"""
Unit tests for cart bundle discount calculations.
Verifies that discounts apply strictly to bundle items only and not incomplete bundles.
"""

from unittest.mock import patch
import pandas as pd
import pytest
from backend.cart import calculate_discount


@pytest.fixture
def mock_rules_df():
    """Mock rules DataFrame with a bundle of ITEM A and ITEM B."""
    return pd.DataFrame({
        "antecedents": ["ITEM A"],
        "consequents": ["ITEM B"],
        "support": [0.05],
        "confidence": [0.60],
        "lift": [1.8]
    })


def test_discount_applies_to_bundle_items_only(mock_rules_df):
    """
    Cart has:
    - ITEM A: quantity 2 @ £10.00 = £20.00
    - ITEM B: quantity 1 @ £15.00 = £15.00
    - ITEM C (not in bundle): quantity 1 @ £50.00 = £50.00
    Total subtotal = £85.00
    Bundle line total (ITEM A + ITEM B) = £35.00
    Rule confidence=0.60, lift=1.8 -> 10% discount.
    Expected discount = 10% of £35.00 = £3.50 (NOT 10% of £85.00).
    """
    cart_items = [
        {"name": "ITEM A", "quantity": 2, "subtotal": 20.00},
        {"name": "ITEM B", "quantity": 1, "subtotal": 15.00},
        {"name": "ITEM C", "quantity": 1, "subtotal": 50.00},
    ]

    with patch("backend.cart.load_rules", return_value=mock_rules_df):
        discount_amount, tier, reason = calculate_discount(cart_items)

    assert discount_amount == 3.50
    assert tier == "Strong Relationship"
    assert reason is not None


def test_no_discount_when_bundle_is_incomplete(mock_rules_df):
    """
    Cart has ITEM A and ITEM C, but is missing ITEM B.
    Bundle is incomplete, so no discount should be applied.
    """
    cart_items = [
        {"name": "ITEM A", "quantity": 2, "subtotal": 20.00},
        {"name": "ITEM C", "quantity": 1, "subtotal": 50.00},
    ]

    with patch("backend.cart.load_rules", return_value=mock_rules_df):
        discount_amount, tier, reason = calculate_discount(cart_items)

    assert discount_amount == 0.0
    assert tier is None
    assert reason is None
