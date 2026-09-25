"""
Visualization Module for Online Retail Association Mining.
Provides matplotlib, seaborn, and interactive Plotly figures for project
reporting and Streamlit dashboards.
"""

from typing import Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


def plot_top_products_matplotlib(top_products_df: pd.DataFrame, n: int = 15):
    """Matplotlib/Seaborn bar chart of top products."""
    data = top_products_df.head(n)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=data,
        x="Transaction_Count",
        y="Description",
        palette="viridis",
        ax=ax
    )
    ax.set_title(f"Top {n} Most Frequently Purchased Products", fontsize=14, weight="bold")
    ax.set_xlabel("Number of Transactions", fontsize=11)
    ax.set_ylabel("Product Description", fontsize=11)
    plt.tight_layout()
    return fig


def plot_top_products_plotly(top_products_df: pd.DataFrame, n: int = 15):
    """Interactive Plotly horizontal bar chart of top products."""
    data = top_products_df.head(n).iloc[::-1]  # Reverse for top-down display
    fig = px.bar(
        data,
        x="Transaction_Count",
        y="Description",
        orientation="h",
        text="Transaction_Count",
        color="Support",
        color_continuous_scale="Viridis",
        title=f"Top {n} Most Frequently Purchased Products",
        labels={"Transaction_Count": "Transactions", "Description": "Product", "Support": "Support"}
    )
    fig.update_layout(
        template="plotly_dark",
        height=520,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Number of Transactions",
        yaxis_title=""
    )
    return fig


def plot_basket_size_plotly(basket_sizes_series: pd.Series, max_size: int = 30):
    """Plotly distribution of products per shopping basket."""
    # Clip large basket sizes for clean visualization
    clipped = basket_sizes_series.clip(upper=max_size)
    counts = clipped.value_counts().sort_index().reset_index()
    counts.columns = ["Items_Per_Basket", "Frequency"]
    counts["Label"] = counts["Items_Per_Basket"].astype(str)
    counts.loc[counts["Items_Per_Basket"] == max_size, "Label"] = f"{max_size}+"

    fig = px.bar(
        counts,
        x="Label",
        y="Frequency",
        title="Distribution of Basket Sizes (Products per Transaction)",
        labels={"Label": "Number of Unique Products", "Frequency": "Transaction Count"},
        color="Frequency",
        color_continuous_scale="Teal"
    )
    fig.update_layout(
        template="plotly_dark",
        height=420,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Products in Basket",
        yaxis_title="Transactions"
    )
    return fig


def plot_support_vs_confidence_plotly(rules_df: pd.DataFrame):
    """Interactive scatter plot of Support vs Confidence colored by Lift."""
    if rules_df.empty:
        return go.Figure()

    sample_df = rules_df.sample(min(len(rules_df), 1500), random_state=42) if len(rules_df) > 1500 else rules_df

    hover_text = (
        "<b>Rule:</b> " + sample_df["rule_str"] + "<br>" +
        "<b>Support:</b> " + sample_df["support"].round(4).astype(str) + "<br>" +
        "<b>Confidence:</b> " + (sample_df["confidence"] * 100).round(1).astype(str) + "%<br>" +
        "<b>Lift:</b> " + sample_df["lift"].round(2).astype(str)
    )

    fig = px.scatter(
        sample_df,
        x="support",
        y="confidence",
        color="lift",
        color_continuous_scale="Plasma",
        title="Association Rules: Support vs Confidence (Color = Lift)",
        labels={"support": "Support", "confidence": "Confidence", "lift": "Lift"},
        opacity=0.8
    )
    fig.update_traces(hoverinfo="text", hovertext=hover_text, marker=dict(size=8))
    fig.update_layout(
        template="plotly_dark",
        height=500,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Support (Transaction Co-occurrence Frequency)",
        yaxis_title="Confidence (Conditional Purchase Probability)"
    )
    return fig


def plot_confidence_vs_lift_plotly(rules_df: pd.DataFrame):
    """Interactive scatter plot of Confidence vs Lift colored by Support."""
    if rules_df.empty:
        return go.Figure()

    sample_df = rules_df.sample(min(len(rules_df), 1500), random_state=42) if len(rules_df) > 1500 else rules_df

    hover_text = (
        "<b>Rule:</b> " + sample_df["rule_str"] + "<br>" +
        "<b>Support:</b> " + sample_df["support"].round(4).astype(str) + "<br>" +
        "<b>Confidence:</b> " + (sample_df["confidence"] * 100).round(1).astype(str) + "%<br>" +
        "<b>Lift:</b> " + sample_df["lift"].round(2).astype(str)
    )

    fig = px.scatter(
        sample_df,
        x="confidence",
        y="lift",
        color="support",
        color_continuous_scale="Turbo",
        title="Association Rules: Confidence vs Lift (Color = Support)",
        labels={"confidence": "Confidence", "lift": "Lift", "support": "Support"},
        opacity=0.8
    )
    fig.update_traces(hoverinfo="text", hovertext=hover_text, marker=dict(size=8))
    fig.update_layout(
        template="plotly_dark",
        height=500,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Confidence (Conditional Probability)",
        yaxis_title="Lift (Association Strength Ratio)"
    )
    return fig


def plot_discount_distribution_plotly(bundles_df: pd.DataFrame):
    """Plot distribution of recommended discounts across generated bundles."""
    if bundles_df.empty or "discount_tier" not in bundles_df.columns:
        return go.Figure()

    tier_counts = bundles_df["discount_tier"].value_counts().reset_index()
    tier_counts.columns = ["Discount Tier", "Count"]

    color_map = {
        "Very Strong Relationship": "#00CC96",
        "Strong Relationship": "#636EFA",
        "Moderate Relationship": "#FFA15A",
        "Weak Relationship / No Discount": "#EF553B"
    }

    fig = px.pie(
        tier_counts,
        names="Discount Tier",
        values="Count",
        title="Distribution of Bundles by Recommended Discount Tier",
        color="Discount Tier",
        color_discrete_map=color_map,
        hole=0.45
    )
    fig.update_layout(
        template="plotly_dark",
        height=420,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig
