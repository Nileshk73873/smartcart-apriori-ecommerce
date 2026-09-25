"""
Unit tests for data preprocessing module.
"""

import pandas as pd
import pytest
from src.preprocessing import clean_retail_data


@pytest.fixture
def sample_raw_data():
    """Create a controlled sample dataset with intentional dirty data."""
    return pd.DataFrame({
        "Invoice": [
            "536365", "536365", "536365",  # Valid invoice with 3 items
            "C536379",                     # Cancelled invoice
            "536380",                      # Negative quantity
            "536381",                      # Zero price
            "536382",                      # Missing description
            "536383",                      # Whitespace only description
            "536384",                      # Valid row without Customer ID
            "536365", "536365", "536365"   # Exact duplicate rows
        ],
        "StockCode": [
            "85123A", "71053", "84406B",
            "D",
            "22838",
            "22839",
            "22840",
            "22841",
            "22842",
            "85123A", "71053", "84406B"
        ],
        "Description": [
            "WHITE HANGING HEART T-LIGHT HOLDER",
            "WHITE METAL LANTERN",
            "CREAM CUPID HEARTS COAT HANGER",
            "Discount",
            "T-LIGHT HOLDER",
            "FAIRY CAKE FLOCK",
            None,
            "   ",
            "CERAMIC STRAWBERRY CAKE",
            "WHITE HANGING HEART T-LIGHT HOLDER",
            "WHITE METAL LANTERN",
            "CREAM CUPID HEARTS COAT HANGER"
        ],
        "Quantity": [6, 6, 8, -1, -5, 10, 5, 2, 4, 6, 6, 8],
        "InvoiceDate": ["2010-12-01 08:26:00"] * 12,
        "Price": [2.55, 3.39, 2.75, 27.50, 4.25, 0.00, 1.95, 2.10, 3.75, 2.55, 3.39, 2.75],
        "Customer ID": [17850.0, 17850.0, 17850.0, 14527.0, 15311.0, 16000.0, 17000.0, 17001.0, None, 17850.0, 17850.0, 17850.0],
        "Country": ["United Kingdom"] * 12
    })


def test_clean_retail_data_removes_cancelled(sample_raw_data):
    cleaned, stats = clean_retail_data(sample_raw_data, save_output=False)
    assert not cleaned["Invoice"].str.startswith("C").any(), "Cancelled invoices should be removed"
    assert stats["cancelled_removed"] == 1


def test_clean_retail_data_removes_negative_quantity(sample_raw_data):
    cleaned, stats = clean_retail_data(sample_raw_data, save_output=False)
    assert (cleaned["Quantity"] > 0).all(), "Quantities must be strictly greater than 0"
    assert stats["invalid_qty_removed"] == 1


def test_clean_retail_data_removes_zero_or_negative_price(sample_raw_data):
    cleaned, stats = clean_retail_data(sample_raw_data, save_output=False)
    assert (cleaned["Price"] > 0).all(), "Prices must be strictly greater than 0"
    assert stats["invalid_price_removed"] == 1


def test_clean_retail_data_removes_missing_description(sample_raw_data):
    cleaned, stats = clean_retail_data(sample_raw_data, save_output=False)
    assert not cleaned["Description"].isnull().any(), "Missing descriptions must be removed"
    assert not (cleaned["Description"] == "").any(), "Empty string descriptions must be removed"


def test_clean_retail_data_retains_missing_customer_id(sample_raw_data):
    cleaned, _ = clean_retail_data(sample_raw_data, save_output=False)
    # Row with Invoice 536384 has missing Customer ID but valid product and transaction
    assert "536384" in cleaned["Invoice"].values, "Valid transactions with missing Customer ID must be retained"


def test_clean_retail_data_removes_duplicates(sample_raw_data):
    cleaned, stats = clean_retail_data(sample_raw_data, save_output=False)
    assert stats["duplicates_removed"] == 3
    # Exactly 4 valid unique rows remain (3 from 536365 + 1 from 536384)
    assert len(cleaned) == 4
