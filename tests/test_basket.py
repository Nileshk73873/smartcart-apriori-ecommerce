"""
Unit tests for basket creation and descriptive analysis.
"""

import pandas as pd
import pytest
from src.basket import create_basket_matrix, analyze_baskets


@pytest.fixture
def sample_clean_df():
    return pd.DataFrame({
        "Invoice": ["INV1", "INV1", "INV1", "INV2", "INV2", "INV3"],
        "Description": ["Product A", "Product B", "Product A", "Product B", "Product C", "Product A"],
        "Quantity": [2, 1, 3, 1, 5, 2],
        "Price": [10.0, 15.0, 10.0, 15.0, 20.0, 10.0],
        "Country": ["United Kingdom"] * 6,
        "InvoiceDate": ["2010-12-01"] * 6
    })


def test_basket_matrix_binary_values(sample_clean_df):
    basket = create_basket_matrix(sample_clean_df, as_bool=True)
    # Check shape
    assert basket.shape == (3, 3)
    # Check that values are strictly boolean
    assert basket.dtypes.apply(lambda dt: dt == bool).all()
    # Check that multiple purchases of Product A in INV1 become True (1)
    assert basket.loc["INV1", "Product A"] is True or basket.loc["INV1", "Product A"] == 1
    assert basket.loc["INV1", "Product B"] is True or basket.loc["INV1", "Product B"] == 1
    assert basket.loc["INV1", "Product C"] is False or basket.loc["INV1", "Product C"] == 0


def test_basket_analysis_metrics(sample_clean_df):
    stats = analyze_baskets(sample_clean_df)
    assert stats["total_transactions"] == 3
    assert stats["total_unique_products"] == 3
    # Invoices: INV1 has 2 unique items (A, B), INV2 has 2 unique items (B, C), INV3 has 1 unique item (A)
    # Mean: (2 + 2 + 1) / 3 = 5/3 = 1.67
    assert stats["avg_products_per_basket"] == 1.67
    assert stats["min_products_per_basket"] == 1
    assert stats["max_products_per_basket"] == 2
