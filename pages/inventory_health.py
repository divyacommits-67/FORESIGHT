import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path



# Load Data

BASE_DIR = Path(__file__).resolve().parent.parent

inventory_path = BASE_DIR / "dashboard_data" / "inventory_risk.csv"

inventory_df = pd.read_csv(inventory_path)

inventory_df["Snapshot_Date"] = pd.to_datetime(
    inventory_df["Snapshot_Date"]
)



# Page Header

st.title("Inventory Health")

st.write(
    "A consolidated view of inventory value, stock coverage, "
    "and reorder-point position across the active SKU portfolio."
)

snapshot_date = inventory_df["Snapshot_Date"].max()

st.caption(
    f"Inventory position as of {snapshot_date.strftime('%d %b %Y')}"
)



# Inventory Metrics

total_inventory_value = inventory_df["Current_Inventory_Value"].sum()

avg_stock_coverage = inventory_df[
    "Total_Stock_Coverage_Days"
].mean()

below_reorder = (
    inventory_df["Current_Stock"]
    < inventory_df["Reorder_Point"]
).sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Inventory Value",
        f"₹{total_inventory_value / 10000000:.2f} Cr"
    )

with col2:
    st.metric(
        "Avg Total Stock Coverage",
        f"{avg_stock_coverage:.1f} days"
    )

with col3:
    st.metric(
        "SKUs Below Reorder Point",
        f"{below_reorder}"
    )



# Inventory Value by Category

st.markdown("### Inventory Value by Category")

category_inventory = (
    inventory_df
    .groupby("Category", as_index=False)["Current_Inventory_Value"]
    .sum()
    .sort_values("Current_Inventory_Value", ascending=True)
)

fig_value = go.Figure()

fig_value.add_trace(
    go.Bar(
        x=category_inventory["Current_Inventory_Value"],
        y=category_inventory["Category"],
        orientation="h",
        marker_color="#315C8C",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Inventory Value: ₹%{x:,.0f}"
            "<extra></extra>"
        )
    )
)

fig_value.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(color="#1F2933"),
    xaxis=dict(
        title=dict(
            text="Inventory Value (₹)",
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
    fig_value,
    use_container_width=True
)

st.write(
    "Inventory value varies substantially across categories, "
    "helping identify where the largest amount of capital is "
    "currently tied up in stock."
)



# Reorder Point Analysis

st.markdown("### Current Stock vs Reorder Point")

reorder_analysis = inventory_df.copy()

reorder_analysis["Reorder_Gap"] = (
    reorder_analysis["Current_Stock"]
    - reorder_analysis["Reorder_Point"]
)

reorder_analysis = (
    reorder_analysis
    .sort_values("Reorder_Gap")
    .head(10)
    .sort_values("Reorder_Gap", ascending=True)
)

fig_reorder = go.Figure()

fig_reorder.add_trace(
    go.Bar(
        x=reorder_analysis["Current_Stock"],
        y=reorder_analysis["SKU"],
        name="Current Stock",
        orientation="h",
        marker_color="#315C8C",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Current Stock: %{x:,.0f} units"
            "<extra></extra>"
        )
    )
)

fig_reorder.add_trace(
    go.Bar(
        x=reorder_analysis["Reorder_Point"],
        y=reorder_analysis["SKU"],
        name="Reorder Point",
        orientation="h",
        marker_color="#9A7B4F",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Reorder Point: %{x:,.0f} units"
            "<extra></extra>"
        )
    )
)

fig_reorder.update_layout(
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
            text="Units",
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
            text="SKU",
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
    fig_reorder,
    use_container_width=True
)

st.write(
    "The comparison highlights SKUs where current stock is "
    "closest to, or below, the defined reorder point. The "
    "reorder point is an inventory planning threshold and "
    "should be interpreted alongside demand forecasts, "
    "lead time, and safety stock."
)