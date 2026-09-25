"""
Main Execution Script for Online Retail Association Rule Mining Project.
Executes the complete end-to-end data mining and recommendation pipeline.

Usage:
    python main.py
"""

import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_dataset, inspect_raw_dataset, print_dataset_report
from src.preprocessing import clean_retail_data
from src.basket import create_basket_matrix, analyze_baskets
from src.apriori_model import run_apriori
from src.association_rules import generate_rules, filter_strong_rules
from src.recommendations import generate_bundle_recommendations, recommend_products


def main():
    total_start = time.time()
    print("\n" + "=" * 70)
    print("  SMART PRODUCT BUNDLING & DISCOUNT RECOMMENDATION SYSTEM")
    print("  Data Mining Mini Project - Apriori Association Rule Mining")
    print("=" * 70 + "\n")

    # ---------------------------------------------------------
    # STEP 1: LOAD RAW DATASET
    # ---------------------------------------------------------
    print("[1/7] Loading Raw Dataset...")
    df_raw = load_dataset()

    # ---------------------------------------------------------
    # STEP 2: RAW DATASET INSPECTION & DIAGNOSTIC REPORT
    # ---------------------------------------------------------
    print("\n[2/7] Inspecting Raw Dataset Statistics...")
    raw_summary = inspect_raw_dataset(df_raw)
    print_dataset_report(raw_summary)

    # ---------------------------------------------------------
    # STEP 3: PREPROCESSING & DATA CLEANING
    # ---------------------------------------------------------
    print("\n[3/7] Cleaning Data for Association Rule Mining...")
    t_clean = time.time()
    df_cleaned, clean_stats = clean_retail_data(
        df_raw,
        save_output=True,
        output_path="data/processed/cleaned_retail.csv"
    )
    print(f"Data cleaned in {time.time() - t_clean:.2f} seconds.")
    print(f" - Rows before cleaning:      {clean_stats['rows_before']:,}")
    print(f" - Rows after cleaning:       {clean_stats['rows_after']:,}")
    print(f" - Removed:                   {clean_stats['rows_removed']:,} ({clean_stats['percentage_removed']}%)")
    print(f" - Unique Invoices (Baskets): {clean_stats['unique_invoices']:,}")
    print(f" - Unique Products:           {clean_stats['unique_products']:,}")
    print(" - Saved cleaned dataset to:  data/processed/cleaned_retail.csv")

    # Free raw dataframe memory
    del df_raw

    # ---------------------------------------------------------
    # STEP 4: BASKET CREATION & DESCRIPTIVE ANALYSIS
    # ---------------------------------------------------------
    print("\n[4/7] Generating Transaction Basket Matrix & Descriptive Metrics...")
    t_basket = time.time()
    basket_stats = analyze_baskets(df_cleaned)
    print(f" - Total Transactions:        {basket_stats['total_transactions']:,}")
    print(f" - Total Unique Products:     {basket_stats['total_unique_products']:,}")
    print(f" - Products / Basket (Mean):  {basket_stats['avg_products_per_basket']}")
    print(f" - Products / Basket (Median):{basket_stats['median_products_per_basket']}")
    print(f" - Products / Basket (Min):   {basket_stats['min_products_per_basket']}")
    print(f" - Products / Basket (Max):   {basket_stats['max_products_per_basket']}")

    # Build binary basket matrix
    basket_df = create_basket_matrix(df_cleaned, as_bool=True)
    print(f"Basket matrix built in {time.time() - t_basket:.2f} seconds.")

    # ---------------------------------------------------------
    # STEP 5: RUN APRIORI ALGORITHM
    # ---------------------------------------------------------
    MIN_SUPPORT = 0.01  # Configurable threshold (1% of transactions = ~401 baskets)
    print(f"\n[5/7] Running Apriori Algorithm (MIN_SUPPORT = {MIN_SUPPORT:.2%})...")
    t_apriori = time.time()
    frequent_itemsets = run_apriori(
        basket_df,
        min_support=MIN_SUPPORT,
        save_output=True,
        output_path="outputs/frequent_itemsets.csv"
    )
    print(f"Apriori execution completed in {time.time() - t_apriori:.2f} seconds.")
    print(f" - Total Frequent Itemsets:   {len(frequent_itemsets):,}")
    print(f" - Itemset size breakdown:    {frequent_itemsets['length'].value_counts().to_dict()}")
    print(" - Saved itemsets to:         outputs/frequent_itemsets.csv")

    # ---------------------------------------------------------
    # STEP 6: GENERATE & FILTER ASSOCIATION RULES
    # ---------------------------------------------------------
    MIN_CONFIDENCE = 0.30
    MIN_LIFT = 1.20
    print(f"\n[6/7] Generating Association Rules (MIN_CONFIDENCE={MIN_CONFIDENCE}, MIN_LIFT={MIN_LIFT})...")
    t_rules = time.time()
    all_rules = generate_rules(
        frequent_itemsets,
        metric="lift",
        min_threshold=1.0,
        save_output=True,
        output_path="outputs/association_rules.csv"
    )
    strong_rules = filter_strong_rules(
        all_rules,
        min_confidence=MIN_CONFIDENCE,
        min_lift=MIN_LIFT,
        sort_by="lift",
        save_output=True,
        output_path="outputs/strong_association_rules.csv"
    )
    print(f"Rules generated in {time.time() - t_rules:.2f} seconds.")
    print(f" - Total Association Rules:   {len(all_rules):,}")
    print(f" - Strong Rules Filtered:     {len(strong_rules):,}")
    print(" - Saved all rules to:        outputs/association_rules.csv")
    print(" - Saved strong rules to:     outputs/strong_association_rules.csv")

    # ---------------------------------------------------------
    # STEP 7: BUNDLE RECOMMENDATIONS & DISCOUNT ASSIGNMENTS
    # ---------------------------------------------------------
    print("\n[7/7] Generating Product Bundle & Discount Recommendations...")
    t_bundles = time.time()
    bundles_df = generate_bundle_recommendations(
        strong_rules,
        min_confidence=MIN_CONFIDENCE,
        min_lift=MIN_LIFT,
        save_output=True,
        output_path="outputs/bundle_recommendations.csv"
    )
    print(f"Bundles created in {time.time() - t_bundles:.2f} seconds.")
    print(f" - Unique Bundles Generated:  {len(bundles_df):,}")
    print(" - Saved recommendations to:  outputs/bundle_recommendations.csv")

    # ---------------------------------------------------------
    # DISPLAY KEY RESULTS & HIGHLIGHTS
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("  EXEMPLARY HIGH-LIFT ASSOCIATION RULES")
    print("=" * 70)
    sample_rules = strong_rules.head(5)
    for idx, row in sample_rules.iterrows():
        print(f"\nRule #{idx+1}:")
        print(f"  {row['rule_str']}")
        print(f"  Support:    {row['support']:.4f} ({row['support']*100:.2f}%)")
        print(f"  Confidence: {row['confidence']:.4f} ({row['confidence']*100:.2f}%)")
        print(f"  Lift:       {row['lift']:.2f}x co-occurrence boost")

    print("\n" + "=" * 70)
    print("  EXEMPLARY RECOMMENDED PRODUCT BUNDLES WITH DISCOUNT LOGIC")
    print("=" * 70)
    sample_bundles = bundles_df.head(5)
    for idx, row in sample_bundles.iterrows():
        print(f"\nBundle #{idx+1}: {row['bundle_name']}")
        print(f"  Primary:    {row['primary_item(s)']}")
        print(f"  Complement: {row['complementary_item(s)']}")
        print(f"  Metrics:    Support={row['support']:.4f}, Confidence={row['confidence']:.2%}, Lift={row['lift']:.2f}")
        print(f"  Discount:   {row['suggested_discount_pct']:.0f}% ({row['discount_tier']})")
        print(f"  Rationale:  {row['business_rationale']}")

    # Interactive test recommendation
    test_prod = "WHITE HANGING HEART T-LIGHT HOLDER"
    print("\n" + "-" * 70)
    print(f"Testing Recommendation Engine for: '{test_prod}'")
    rec_result = recommend_products(test_prod, strong_rules, top_n=3)
    for r in rec_result["recommendations"]:
        print(f" -> Recommend: {r['recommended_product']} (Confidence: {r['confidence']:.1%}, Lift: {r['lift']}x, Discount: {r['suggested_discount_pct']:.0f}%)")

    total_time = time.time() - total_start
    print("\n" + "=" * 70)
    print(f"  PIPELINE EXECUTION COMPLETED SUCCESSFULLY IN {total_time:.2f} SECONDS!")
    print("=" * 70)
    print("\nGenerated Output Files:")
    print("  1. data/processed/cleaned_retail.csv")
    print("  2. outputs/frequent_itemsets.csv")
    print("  3. outputs/association_rules.csv")
    print("  4. outputs/strong_association_rules.csv")
    print("  5. outputs/bundle_recommendations.csv")
    print("\nTo launch the interactive dashboard, run:")
    print("    streamlit run app.py\n")


if __name__ == "__main__":
    main()
