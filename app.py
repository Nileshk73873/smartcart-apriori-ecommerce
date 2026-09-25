"""
Streamlit Web Dashboard for Online Retail Association Rule Mining.
Smart Product Bundling and Discount Recommendation System.

Run via:
    streamlit run app.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np

from src.data_loader import load_dataset, inspect_raw_dataset
from src.preprocessing import clean_retail_data
from src.basket import create_basket_matrix, analyze_baskets
from src.apriori_model import run_apriori
from src.association_rules import generate_rules, filter_strong_rules
from src.discount import calculate_bundle_discount, DEFAULT_DISCOUNT_RULES, DISCLAIMER_TEXT
from src.recommendations import recommend_products, generate_bundle_recommendations, find_matching_products
from src.visualization import (
    plot_top_products_plotly,
    plot_basket_size_plotly,
    plot_support_vs_confidence_plotly,
    plot_confidence_vs_lift_plotly,
    plot_discount_distribution_plotly
)

# -----------------------------------------------------------------------------
# STREAMLIT PAGE CONFIG & THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Bundling & Discount Engine | Apriori Mining",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, premium appearance
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        padding: 24px;
        border-radius: 14px;
        color: #ffffff;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .kpi-card {
        background: #181926;
        border: 1px solid #2e3148;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #6366f1;
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .kpi-subtitle {
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 4px;
    }
    
    .bundle-badge-5 {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid #059669;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .bundle-badge-10 {
        background: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        border: 1px solid #4f46e5;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .bundle-badge-15 {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid #d97706;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    .disclaimer-box {
        background: rgba(30, 41, 59, 0.8);
        border-left: 4px solid #f59e0b;
        padding: 14px 18px;
        border-radius: 6px;
        color: #cbd5e1;
        font-size: 0.88rem;
        margin-top: 14px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# CACHED DATA PIPELINE FUNCTIONS
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading and verifying dataset...")
def get_clean_data():
    """Load and preprocess dataset, leveraging disk cache when available."""
    cleaned_csv = Path("data/processed/cleaned_retail.csv")
    if cleaned_csv.is_file():
        df = pd.read_csv(
            cleaned_csv,
            dtype={"Invoice": str, "StockCode": str, "Description": str, "Country": str}
        )
        return df
    # Fallback: process from raw
    raw_df = load_dataset()
    cleaned_df, _ = clean_retail_data(raw_df, save_output=True)
    return cleaned_df


@st.cache_data(show_spinner="Analyzing transaction baskets...")
def get_basket_metrics(df_clean):
    return analyze_baskets(df_clean)


@st.cache_data(show_spinner="Building basket matrix...")
def get_basket_matrix(df_clean, min_item_freq=None):
    return create_basket_matrix(df_clean, min_item_frequency=min_item_freq, as_bool=True)


@st.cache_data(show_spinner="Mining frequent itemsets with Apriori...")
def get_frequent_itemsets(basket_matrix, min_sup):
    return run_apriori(basket_matrix, min_support=min_sup, save_output=False)


@st.cache_data(show_spinner="Generating association rules...")
def get_rules(itemsets, min_conf, min_lift, sort_metric="lift"):
    all_r = generate_rules(itemsets, metric="lift", min_threshold=1.0, save_output=False)
    strong_r = filter_strong_rules(
        all_r,
        min_confidence=min_conf,
        min_lift=min_lift,
        sort_by=sort_metric,
        save_output=False
    )
    return all_r, strong_r


@st.cache_data(show_spinner="Formulating product bundles...")
def get_bundles(strong_r, min_conf, min_lift):
    return generate_bundle_recommendations(
        strong_r,
        min_confidence=min_conf,
        min_lift=min_lift,
        save_output=False
    )


# -----------------------------------------------------------------------------
# LOAD PIPELINE DATA
# -----------------------------------------------------------------------------
try:
    df_clean = get_clean_data()
    basket_stats = get_basket_metrics(df_clean)
except Exception as e:
    st.error(f"Error loading data pipeline: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Model Parameters")
    st.markdown("Tune thresholds for Apriori association rule generation:")

    min_support = st.slider(
        "Minimum Support (min_support)",
        min_value=0.005,
        max_value=0.050,
        value=0.010,
        step=0.005,
        format="%.3f",
        help="Fraction of transactions that must contain the itemset (e.g. 0.010 = 1% ≈ 401 baskets)."
    )

    min_confidence = st.slider(
        "Minimum Confidence (min_confidence)",
        min_value=0.10,
        max_value=0.90,
        value=0.30,
        step=0.05,
        format="%.2f",
        help="Minimum conditional probability P(Consequent | Antecedent)."
    )

    min_lift = st.slider(
        "Minimum Lift (min_lift)",
        min_value=1.0,
        max_value=10.0,
        value=1.20,
        step=0.1,
        format="%.2f",
        help="Minimum lift ratio. Values > 1.0 indicate positive association."
    )

    sort_metric = st.selectbox(
        "Sort Rules & Recommendations By",
        options=["lift", "confidence", "support"],
        index=0,
        format_func=lambda x: f"{x.capitalize()} (Descending)"
    )

    max_recommendations = st.slider(
        "Top Recommendations to Show",
        min_value=1,
        max_value=15,
        value=5
    )

    st.markdown("---")
    st.markdown("### 💡 Business Rules for Bundles")
    st.markdown(
        """
        - **5% Discount**: Conf ≥ 70% & Lift ≥ 2.0  
          *(Very High Affinity)*
        - **10% Discount**: Conf ≥ 50% & Lift ≥ 1.5  
          *(Strong Affinity)*
        - **15% Discount**: Conf ≥ 30% & Lift ≥ 1.2  
          *(Moderate Affinity)*
        """
    )
    st.caption("Heuristic business logic; not mathematically profit-optimized.")


# Run Apriori & Rule Generation with selected thresholds
# Notice: For interactive responsiveness, pre-filtering items that have individual support < min_support
# preserves exact mathematical equivalence while boosting speed
min_invoice_freq = int(min_support * basket_stats["total_transactions"])
basket_matrix = get_basket_matrix(df_clean, min_item_freq=min_invoice_freq)
frequent_itemsets = get_frequent_itemsets(basket_matrix, min_sup=min_support)
all_rules, strong_rules = get_rules(frequent_itemsets, min_conf=min_confidence, min_lift=min_lift, sort_metric=sort_metric)
bundles_df = get_bundles(strong_rules, min_conf=min_confidence, min_lift=min_lift)


# -----------------------------------------------------------------------------
# MAIN HEADER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:2.2rem; font-weight:700;">🛍️ Smart Product Bundling & Discount Recommendation</h1>
    <p style="margin:6px 0 0 0; font-size:1.05rem; opacity:0.9;">
        End-to-End Market Basket Analysis using Apriori Association Rule Mining on Online Retail II Transactions
    </p>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# DASHBOARD TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Overview",
    "🛒 Basket Profile",
    "🔍 Frequent Itemsets",
    "⚡ Association Rules",
    "🎯 Product Recommender",
    "📦 Bundle Packages",
    "📈 Analytics & Viva Guide"
])

# -----------------------------------------------------------------------------
# TAB 1: OVERVIEW & KPIS
# -----------------------------------------------------------------------------
with tab1:
    st.markdown("### 📈 Executive Performance & Mining Summary")

    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

    with kpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Transactions</div>
            <div class="kpi-value">{basket_stats['total_transactions']:,}</div>
            <div class="kpi-subtitle">Unique Invoices</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Catalog Items</div>
            <div class="kpi-value">{basket_stats['total_unique_products']:,}</div>
            <div class="kpi-subtitle">Unique Products</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Basket Size</div>
            <div class="kpi-value">{basket_stats['avg_products_per_basket']}</div>
            <div class="kpi-subtitle">Items / Transaction</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Frequent Itemsets</div>
            <div class="kpi-value">{len(frequent_itemsets):,}</div>
            <div class="kpi-subtitle">Support ≥ {min_support:.2%}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Strong Rules</div>
            <div class="kpi-value">{len(strong_rules):,}</div>
            <div class="kpi-subtitle">Conf ≥ {min_confidence:.0%}, Lift ≥ {min_lift:.1f}</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Product Bundles</div>
            <div class="kpi-value">{len(bundles_df):,}</div>
            <div class="kpi-subtitle">Discount Eligible</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### 🎯 Business Problem & Solution Architecture")
        st.markdown("""
        Retailers frequently struggle with:
        1. **Ineffective Cross-Selling**: Showing arbitrary or generic recommendations that do not reflect organic shopper affinities.
        2. **Excessive Margin Erosion**: Offering blanket store-wide discounts instead of targeted promotions.
        3. **Inventory Imbalance**: Slow-moving complementary goods staying on shelves.

        **Our Solution Architecture:**
        - **Apriori Association Rule Mining**: Mines empirical co-purchase probabilities (Support, Confidence, Lift) across 40,000+ real transactions.
        - **Algorithmic Bundling**: Pairs high-affinity antecedents with consequents into multi-item bundles.
        - **Discount Business Rules**: Dynamically assigns tiered discounts (5%, 10%, 15%) reflecting relationship strength.
        """)

    with col_right:
        st.markdown("#### 📋 Core Metric Glossary")
        st.markdown("""
        - **Support ($P(A \\cap B)$)**: Proportion of all transactions containing both products $A$ and $B$.
        - **Confidence ($P(B|A)$)**: Probability that a customer buys $B$ given that they already put $A$ in their basket.
        - **Lift**: Ratio of observed joint purchase frequency to the expected frequency if $A$ and $B$ were completely independent:
          $$\\text{Lift}(A \\to B) = \\frac{\\text{Confidence}(A \\to B)}{\\text{Support}(B)}$$
          - **Lift > 1**: Positive association (complementary products).
          - **Lift = 1**: Independent (no cross-sell synergy).
          - **Lift < 1**: Negative association (substitute goods).
        """)

    st.markdown(f"""
    <div class="disclaimer-box">
        <strong>⚠️ Crucial Academic & Business Distinction:</strong><br>
        {DISCLAIMER_TEXT}
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 2: PRODUCT & BASKET ANALYSIS
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("### 🛒 Product Frequency & Shopping Basket Distribution")

    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        fig_top = plot_top_products_plotly(basket_stats["top_20_products"], n=15)
        st.plotly_chart(fig_top, use_container_width=True)

    with col_p2:
        fig_size = plot_basket_size_plotly(basket_stats["invoice_basket_sizes"], max_size=25)
        st.plotly_chart(fig_size, use_container_width=True)

    st.markdown("#### 📋 Top 20 Most Frequent Products in Catalog")
    st.dataframe(
        basket_stats["top_20_products"].style.format({
            "Transaction_Count": "{:,}",
            "Support": "{:.2%}"
        }),
        use_container_width=True
    )


# -----------------------------------------------------------------------------
# TAB 3: FREQUENT ITEMSETS
# -----------------------------------------------------------------------------
with tab3:
    st.markdown("### 🔍 Frequent Itemsets (Apriori Mining)")
    st.caption(f"Showing itemsets satisfying min_support ≥ {min_support:.3f} ({min_support*100:.1f}%)")

    if frequent_itemsets.empty:
        st.warning("No itemsets found. Please decrease the minimum support threshold in the sidebar.")
    else:
        fi_col1, fi_col2, fi_col3 = st.columns([1, 1, 2])
        with fi_col1:
            len_filter = st.selectbox(
                "Filter by Itemset Size",
                options=["All Sizes", "1 Item", "2 Items", "3+ Items"]
            )
        with fi_col2:
            sort_ord = st.selectbox("Sort Order", options=["Support (High to Low)", "Support (Low to High)"])
        with fi_col3:
            item_search = st.text_input("Search Item in Itemsets", placeholder="e.g. HEART, TEATIME, BAG...")

        fi_df = frequent_itemsets.copy()
        if len_filter == "1 Item":
            fi_df = fi_df[fi_df["length"] == 1]
        elif len_filter == "2 Items":
            fi_df = fi_df[fi_df["length"] == 2]
        elif len_filter == "3+ Items":
            fi_df = fi_df[fi_df["length"] >= 3]

        if item_search:
            fi_df = fi_df[fi_df["itemsets"].apply(
                lambda s: any(item_search.upper() in str(x).upper() for x in s)
            )]

        ascending = (sort_ord == "Support (Low to High)")
        fi_df = fi_df.sort_values(by="support", ascending=ascending)

        display_fi = fi_df.copy()
        display_fi["itemsets"] = display_fi["itemsets"].apply(lambda s: " + ".join(sorted(list(s))))
        display_fi["support_pct"] = (display_fi["support"] * 100).round(2).astype(str) + "%"

        st.dataframe(
            display_fi[["itemsets", "length", "support", "support_pct"]].rename(columns={
                "itemsets": "Itemset",
                "length": "Itemset Length",
                "support": "Support (Decimal)",
                "support_pct": "Support (%)"
            }),
            use_container_width=True,
            height=450
        )


# -----------------------------------------------------------------------------
# TAB 4: ASSOCIATION RULES
# -----------------------------------------------------------------------------
with tab4:
    st.markdown("### ⚡ Association Rules Explorer")
    st.caption(f"Filtering rules with Confidence ≥ {min_confidence:.2f} and Lift ≥ {min_lift:.2f}")

    if strong_rules.empty:
        st.warning("No association rules found meeting these criteria. Relax the Confidence or Lift filters in the sidebar.")
    else:
        st.markdown(f"**Found {len(strong_rules):,} strong rules** (from {len(all_rules):,} total rules with Lift ≥ 1.0).")

        # Scatter Visualizations
        rcol1, rcol2 = st.columns(2)
        with rcol1:
            fig_sc1 = plot_support_vs_confidence_plotly(strong_rules)
            st.plotly_chart(fig_sc1, use_container_width=True)
        with rcol2:
            fig_sc2 = plot_confidence_vs_lift_plotly(strong_rules)
            st.plotly_chart(fig_sc2, use_container_width=True)

        st.markdown("#### 📋 Filtered Association Rules Table")
        rule_search = st.text_input("Filter Rules by Product Keyword", placeholder="e.g. CAKESTAND, RETROSPOT...")

        display_rules = strong_rules.copy()
        if rule_search:
            display_rules = display_rules[
                display_rules["rule_str"].str.upper().str.contains(rule_search.upper(), regex=False)
            ]

        format_rules = pd.DataFrame({
            "Antecedent(s)": display_rules["antecedents_str"],
            "Consequent(s)": display_rules["consequents_str"],
            "Support": display_rules["support"].apply(lambda x: f"{x:.4f} ({x*100:.2f}%)"),
            "Confidence": display_rules["confidence"].apply(lambda x: f"{x:.2%}"),
            "Lift": display_rules["lift"].round(2),
            "Leverage": display_rules["leverage"].round(4) if "leverage" in display_rules.columns else 0.0,
            "Conviction": display_rules["conviction"].round(2) if "conviction" in display_rules.columns else 0.0
        })

        st.dataframe(format_rules, use_container_width=True, height=450)


# -----------------------------------------------------------------------------
# TAB 5: PRODUCT RECOMMENDER
# -----------------------------------------------------------------------------
with tab5:
    st.markdown("### 🎯 Interactive Product Cross-Sell Recommender")
    st.markdown("Select or search for any product to discover its top complementary cross-sell recommendations.")

    all_catalog_products = sorted(list(df_clean["Description"].dropna().unique()))

    # Default popular items
    default_index = 0
    popular_sample = "WHITE HANGING HEART T-LIGHT HOLDER"
    if popular_sample in all_catalog_products:
        default_index = all_catalog_products.index(popular_sample)

    selected_product = st.selectbox(
        "Select Target Product from Catalog:",
        options=all_catalog_products,
        index=default_index,
        help="Type to search through all 5,300+ catalog products."
    )

    if selected_product:
        rec_output = recommend_products(
            product_name=selected_product,
            rules_df=strong_rules,
            sort_by=sort_metric,
            top_n=max_recommendations
        )

        if rec_output["status"] == "no_rules_found":
            st.info(f"ℹ️ {rec_output['message']}")
            st.caption("Tip: This product may have lower purchase support than the current min_support threshold. Try lowering min_support in the sidebar.")
        elif rec_output["recommendations"]:
            st.success(f"Found {len(rec_output['recommendations'])} recommendation(s) for **{selected_product}**:")

            for i, rec in enumerate(rec_output["recommendations"], 1):
                disc_pct = rec["suggested_discount_pct"]
                badge_class = "bundle-badge-5" if disc_pct == 5 else ("bundle-badge-10" if disc_pct == 10 else "bundle-badge-15")

                with st.container():
                    st.markdown(f"""
                    <div style="background:#1e1e2f; border:1px solid #3b3d54; border-radius:10px; padding:18px; margin-bottom:14px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                            <span style="font-size:1.15rem; font-weight:700; color:#ffffff;">
                                #{i}. Complementary Product: <span style="color:#38bdf8;">{rec['recommended_product']}</span>
                            </span>
                            <span class="{badge_class}">
                                Suggested Bundle Discount: {disc_pct:.0f}%
                            </span>
                        </div>
                        <div style="display:flex; gap:24px; color:#cbd5e1; font-size:0.95rem; margin-bottom:10px;">
                            <div><strong>Confidence:</strong> {rec['confidence']:.1%}</div>
                            <div><strong>Lift:</strong> {rec['lift']:.2f}x</div>
                            <div><strong>Support:</strong> {rec['support']:.2%}</div>
                            <div><strong>Tier:</strong> {rec['discount_tier']}</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.03); border-radius:6px; padding:10px 14px; font-size:0.88rem; color:#94a3b8;">
                            <strong>Business Rationale:</strong> {rec['discount_rationale']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 6: BUNDLE PACKAGES & DISCOUNT SIMULATOR
# -----------------------------------------------------------------------------
with tab6:
    st.markdown("### 📦 Recommended Product Bundle Packages")
    st.caption("Pre-configured multi-item bundle opportunities identified from strong association rules.")

    if bundles_df.empty:
        st.warning("No bundle packages could be formulated at current confidence and lift thresholds.")
    else:
        bcol1, bcol2 = st.columns([1, 1])
        with bcol1:
            fig_disc = plot_discount_distribution_plotly(bundles_df)
            st.plotly_chart(fig_disc, use_container_width=True)

        with bcol2:
            st.markdown("#### 🏷️ Bundle Tier Summary")
            tier_summary = bundles_df.groupby("discount_tier").agg(
                Bundle_Count=("bundle_name", "count"),
                Avg_Lift=("lift", "mean"),
                Avg_Confidence=("confidence", "mean")
            ).reset_index()
            tier_summary["Avg_Confidence"] = tier_summary["Avg_Confidence"].apply(lambda x: f"{x:.1%}")
            tier_summary["Avg_Lift"] = tier_summary["Avg_Lift"].round(2)
            st.dataframe(tier_summary, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🛒 Interactive Bundle Price & Savings Simulator")

        bundle_names = bundles_df["bundle_name"].tolist()
        sim_bundle_name = st.selectbox("Select a Bundle to Simulate Pricing:", options=bundle_names[:100])

        if sim_bundle_name:
            chosen_bundle = bundles_df[bundles_df["bundle_name"] == sim_bundle_name].iloc[0]
            disc_pct = chosen_bundle["suggested_discount_pct"]

            sim_col1, sim_col2, sim_col3 = st.columns([1, 1, 1])
            with sim_col1:
                base_price = st.number_input(
                    "Simulated Combined Regular Price (£):",
                    min_value=1.0,
                    max_value=500.0,
                    value=25.0,
                    step=1.0
                )
            with sim_col2:
                discount_amount = base_price * (disc_pct / 100.0)
                final_bundle_price = base_price - discount_amount
                st.metric("Discounted Bundle Price", f"£{final_bundle_price:.2f}", delta=f"-£{discount_amount:.2f} ({disc_pct:.0f}%)")
            with sim_col3:
                st.metric("Customer Savings", f"£{discount_amount:.2f}", delta=f"Tier: {chosen_bundle['discount_tier']}")

            st.info(f"**Strategic Rationale:** {chosen_bundle['business_rationale']}")

        st.markdown("#### 📋 All Recommended Bundles Table")
        st.dataframe(
            bundles_df[[
                "bundle_name", "bundle_size", "support", "confidence", "lift",
                "suggested_discount_pct", "discount_tier"
            ]].rename(columns={
                "bundle_name": "Product Bundle",
                "bundle_size": "Items",
                "support": "Support",
                "confidence": "Confidence",
                "lift": "Lift",
                "suggested_discount_pct": "Discount (%)",
                "discount_tier": "Tier"
            }),
            use_container_width=True,
            height=400
        )


# -----------------------------------------------------------------------------
# TAB 7: ANALYTICS & VIVA GUIDE
# -----------------------------------------------------------------------------
with tab7:
    st.markdown("### 🎓 Academic Defense & Viva Preparation Guide")
    st.markdown("""
    Use these curated questions, answers, and methodological defenses for college presentation and viva evaluation:
    """)

    with st.expander("Q1: What is Market Basket Analysis and how does Apriori solve it?", expanded=True):
        st.markdown("""
        **Answer:**  
        Market Basket Analysis analyzes customer purchasing transactions to discover associations between items placed in the same shopping basket (Invoice).
        The **Apriori algorithm** discovers frequent itemsets based on the **anti-monotonicity property** (or Apriori principle):  
        > *If an itemset is infrequent, then all of its supersets must also be infrequent.*  
        This enables efficient pruning of the exponential search space ($2^k - 1$ possible combinations for $k$ items) without evaluating all itemsets.
        """)

    with st.expander("Q2: What is the exact mathematical difference between Confidence and Lift?", expanded=True):
        st.markdown("""
        **Answer:**  
        - **Confidence** measures directional conditional probability: $P(B|A) = \\frac{\\text{Support}(A \\cap B)}{\\text{Support}(A)}$.  
          A rule can have 90% confidence simply because product $B$ is a ubiquitous bestseller bought by 90% of all customers anyway (e.g. Milk, Bread).
        - **Lift** controls for the baseline popularity of the consequent: $\\text{Lift}(A \\to B) = \\frac{\\text{Confidence}(A \\to B)}{\\text{Support}(B)}$.  
          Lift evaluates how much *more* likely $B$ is purchased when $A$ is present compared to random chance.  
          - If Lift = 1.0, the items are statistically independent.  
          - If Lift > 1.0, there is a true positive co-purchase affinity.
        """)

    with st.expander("Q3: Why doesn't Apriori mathematically calculate the discount percentage?", expanded=True):
        st.markdown("""
        **Answer:**  
        Apriori is an unsupervised pattern-mining algorithm that operates solely on binary transaction presences. It does **not** model:
        1. Profit margins or Cost of Goods Sold (COGS).
        2. Customer price elasticity of demand (how sales volume shifts with price).
        3. Inventory holding costs.  
        Therefore, claiming that Apriori optimizes discounts is methodologically incorrect. Our system strictly treats discount assignment as a **transparent business-rule heuristic** parameterized by Confidence and Lift.
        """)

    with st.expander("Q4: Why was each Invoice used as a transaction instead of Customer ID?"):
        st.markdown("""
        **Answer:**  
        Customer ID aggregates all purchases made by a user across multiple years and different shopping trips. A shopping basket represents products purchased **together in a single trip/checkout session**. Grouping by Customer ID would conflate items bought months apart into the same basket, distorting cross-sell affinity. Furthermore, 22.7% of transactions in the dataset lack a Customer ID (guest checkouts), but have valid Invoices.
        """)

    with st.expander("Q5: What are the primary computational bottlenecks of Apriori and how were they optimized?"):
        st.markdown("""
        **Answer:**  
        With 5,300+ unique products, a dense matrix is $40,077 \\times 5,357 \\approx 214\\text{ million}$ elements.  
        We optimized this using:
        1. **SciPy CSR sparse matrix factorizations** for zero-copy memory efficiency.
        2. **Pre-filtering items below min_support threshold** before candidate combination generation, mathematically exploiting Apriori anti-monotonicity.
        3. **Streamlit session caching (`@st.cache_data`)** for instant UI reactivity.
        """)
