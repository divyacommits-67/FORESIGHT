import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


# Load Data

BASE_DIR = Path(__file__).resolve().parent.parent

decision_path = BASE_DIR / "dashboard_data" / "decision_table.csv"

decision_df = pd.read_csv(decision_path)


# Page Header

st.title("Financial Impact")

st.write(
    "A financial view of inventory exposure, excess stock, "
    "and potential revenue and margin impact identified by "
    "the decision engine."
)



# Financial Metrics

total_excess_value = decision_df[
    "Excess_Inventory_Value"
].sum()

revenue_exposure = decision_df[
    "Potential_Revenue_Exposure"
].sum()

margin_exposure = decision_df[
    "Potential_Gross_Margin_Exposure"
].sum()

reorder_investment = decision_df[
    "Reorder_Investment"
].sum()


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Excess Inventory Value",
        f"₹{total_excess_value / 10000000:.2f} Cr"
    )

with col2:
    st.metric(
        "Potential Revenue Exposure",
        f"₹{revenue_exposure / 10000000:.2f} Cr"
    )

with col3:
    st.metric(
        "Potential Margin Exposure",
        f"₹{margin_exposure / 10000000:.2f} Cr"
    )

with col4:
    st.metric(
        "Reorder Investment",
        f"₹{reorder_investment / 10000000:.2f} Cr"
    )



# Financial Exposure by Category

st.markdown("### Financial Exposure by Category")

category_financial = (
    decision_df
    .groupby("Category", as_index=False)
    .agg(
        Excess_Inventory_Value=(
            "Excess_Inventory_Value",
            "sum"
        ),
        Potential_Revenue_Exposure=(
            "Potential_Revenue_Exposure",
            "sum"
        )
    )
    .sort_values(
        "Excess_Inventory_Value",
        ascending=True
    )
)

fig_category = go.Figure()

fig_category.add_trace(
    go.Bar(
        x=category_financial["Excess_Inventory_Value"],
        y=category_financial["Category"],
        orientation="h",
        name="Excess Inventory Value",
        marker_color="#9A7B4F",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Excess Inventory: ₹%{x:,.0f}"
            "<extra></extra>"
        )
    )
)

fig_category.add_trace(
    go.Bar(
        x=category_financial["Potential_Revenue_Exposure"],
        y=category_financial["Category"],
        orientation="h",
        name="Revenue Exposure",
        marker_color="#315C8C",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Revenue Exposure: ₹%{x:,.0f}"
            "<extra></extra>"
        )
    )
)

fig_category.update_layout(
    height=450,
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(color="#1F2933"),
    barmode="group",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        font=dict(color="#1F2933")
    ),
    xaxis=dict(
        title=dict(
            text="Amount (₹)",
            font=dict(color="#1F2933", size=14)
        ),
        tickfont=dict(
            color="#1F2933",
            size=12
        ),
        gridcolor="#E4E1DB",
        zeroline=False
    ),
    yaxis=dict(
        title=dict(
            text="Category",
            font=dict(color="#1F2933", size=14)
        ),
        tickfont=dict(
            color="#1F2933",
            size=12
        ),
        showgrid=False
    )
)

st.plotly_chart(
    fig_category,
    use_container_width=True
)

st.write(
    "This comparison shows where excess inventory value and "
    "potential revenue exposure are concentrated across the "
    "portfolio. These values represent modelled exposure, "
    "not guaranteed financial losses."
)



# Reorder Investment vs Excess Inventory

st.markdown("### Reorder Investment vs Excess Inventory")

action_financial = (
    decision_df
    .groupby("Recommended_Action", as_index=False)
    .agg(
        Reorder_Investment=(
            "Reorder_Investment",
            "sum"
        ),
        Excess_Inventory_Value=(
            "Excess_Inventory_Value",
            "sum"
        )
    )
)

fig_action = go.Figure()

fig_action.add_trace(
    go.Bar(
        x=action_financial["Recommended_Action"],
        y=action_financial["Reorder_Investment"],
        name="Reorder Investment",
        marker_color="#315C8C",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Reorder Investment: ₹%{y:,.0f}"
            "<extra></extra>"
        )
    )
)

fig_action.add_trace(
    go.Bar(
        x=action_financial["Recommended_Action"],
        y=action_financial["Excess_Inventory_Value"],
        name="Excess Inventory Value",
        marker_color="#9A7B4F",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Excess Inventory: ₹%{y:,.0f}"
            "<extra></extra>"
        )
    )
)

fig_action.update_layout(
    height=450,
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(color="#1F2933"),
    barmode="group",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        font=dict(color="#1F2933")
    ),
    xaxis=dict(
        title=dict(
            text="Recommended Action",
            font=dict(color="#1F2933", size=14)
        ),
        tickfont=dict(
            color="#1F2933",
            size=12
        ),
        showgrid=False
    ),
    yaxis=dict(
        title=dict(
            text="Amount (₹)",
            font=dict(color="#1F2933", size=14)
        ),
        tickfont=dict(
            color="#1F2933",
            size=12
        ),
        gridcolor="#E4E1DB",
        zeroline=False
    )
)

st.plotly_chart(
    fig_action,
    use_container_width=True
)

st.write(
    "The comparison connects recommended operational actions "
    "with their associated financial amounts. Reorder investment "
    "represents modelled purchasing requirements, while excess "
    "inventory value represents stock identified as potentially "
    "above the modelled target level."
)



# Financial Notes

st.markdown("### Interpretation")

st.write(
    "Financial exposure should be interpreted as a decision-support "
    "signal rather than a guaranteed outcome. Revenue and gross-margin "
    "exposure depend on the forecast, inventory position, pricing, "
    "and assumptions used by the decision engine."
)

st.caption(
    "Note: Gross-margin exposure may be negative for SKUs with "
    "negative source-data gross margins. These values are retained "
    "to preserve the underlying data rather than being silently "
    "clamped to zero."
)