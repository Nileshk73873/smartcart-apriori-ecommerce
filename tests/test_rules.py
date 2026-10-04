"""
Unit tests for Apriori frequent itemsets and association rules generation.
Tests hand-computed metrics against algorithm output.
"""

import pandas as pd
import pytest
from src.basket import create_basket_matrix
from src.apriori_model import run_apriori
from src.association_rules import generate_rules


@pytest.fixture
def fixed_basket_df():
    """
    Fixed transaction dataset:
    INV1: ItemA, ItemB
    INV2: ItemA, ItemB, ItemC
    INV3: ItemA, ItemC
    INV4: ItemB, ItemD
    Total = 4 transactions.
    """
    return pd.DataFrame({
        "Invoice": ["INV1", "INV1", "INV2", "INV2", "INV2", "INV3", "INV3", "INV4", "INV4"],
        "Description": [
            "ItemA", "ItemB",
            "ItemA", "ItemB", "ItemC",
            "ItemA", "ItemC",
            "ItemB", "ItemD"
        ],
        "Quantity": [1] * 9,
        "Price": [10.0] * 9,
        "Country": ["UK"] * 9,
        "InvoiceDate": ["2010-12-01"] * 9
    })


def test_apriori_hand_computed_support(fixed_basket_df):
    basket_matrix = create_basket_matrix(fixed_basket_df, as_bool=True)
    # Run with min_support=0.40 (40%)
    itemsets = run_apriori(basket_matrix, min_support=0.40, save_output=False)

    itemset_dict = {
        tuple(sorted(list(row["itemsets"]))): row["support"]
        for _, row in itemsets.iterrows()
    }

    # Hand-computed supports:
    # ItemA appears in INV1, INV2, INV3 -> 3/4 = 0.75
    # ItemB appears in INV1, INV2, INV4 -> 3/4 = 0.75
    # ItemC appears in INV2, INV3 -> 2/4 = 0.50
    # ItemD appears in INV4 -> 1/4 = 0.25 (< 0.40, filtered out)
    # (ItemA, ItemB) appears in INV1, INV2 -> 2/4 = 0.50
    # (ItemA, ItemC) appears in INV2, INV3 -> 2/4 = 0.50

    assert pytest.approx(itemset_dict[("ItemA",)], 0.001) == 0.75
    assert pytest.approx(itemset_dict[("ItemB",)], 0.001) == 0.75
    assert pytest.approx(itemset_dict[("ItemC",)], 0.001) == 0.50
    assert pytest.approx(itemset_dict[("ItemA", "ItemB")], 0.001) == 0.50
    assert pytest.approx(itemset_dict[("ItemA", "ItemC")], 0.001) == 0.50


def test_association_rules_hand_computed_metrics(fixed_basket_df):
    basket_matrix = create_basket_matrix(fixed_basket_df, as_bool=True)
    itemsets = run_apriori(basket_matrix, min_support=0.40, save_output=False)
    rules = generate_rules(itemsets, metric="support", min_threshold=0.40, save_output=False)

    # Find rule ItemC -> ItemA
    # Support(ItemC -> ItemA) = Support(ItemA, ItemC) = 2/4 = 0.50
    # Confidence(ItemC -> ItemA) = 0.50 / Support(ItemC) = 0.50 / 0.50 = 1.0
    # Lift(ItemC -> ItemA) = 1.0 / Support(ItemA) = 1.0 / 0.75 = 4/3 = 1.3333
    rule_c_to_a = rules[
        (rules["antecedents"] == frozenset(["ItemC"])) &
        (rules["consequents"] == frozenset(["ItemA"]))
    ].iloc[0]

    assert pytest.approx(rule_c_to_a["support"], 0.001) == 0.50
    assert pytest.approx(rule_c_to_a["confidence"], 0.001) == 1.00
    assert pytest.approx(rule_c_to_a["lift"], 0.01) == 1.33

    # Find rule ItemA -> ItemB
    # Support(ItemA -> ItemB) = 0.50
    # Confidence(ItemA -> ItemB) = 0.50 / 0.75 = 2/3 ≈ 0.6667
    # Lift(ItemA -> ItemB) = (2/3) / 0.75 = 8/9 ≈ 0.8889
    rule_a_to_b = rules[
        (rules["antecedents"] == frozenset(["ItemA"])) &
        (rules["consequents"] == frozenset(["ItemB"]))
    ].iloc[0]

    assert pytest.approx(rule_a_to_b["support"], 0.001) == 0.50
    assert pytest.approx(rule_a_to_b["confidence"], 0.001) == 2 / 3
    assert pytest.approx(rule_a_to_b["lift"], 0.01) == 8 / 9
