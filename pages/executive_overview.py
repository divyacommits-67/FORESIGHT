import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


# Page Configuration

st.set_page_config(
    page_title="FORESIGHT — Executive Overview",
    page_icon="📊",
    layout="wide"
)

# Paths

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "dashboard_data"


# Load Data

forecast_df = pd.read_csv(
    PROCESSED_DIR / "forecast_4_week.csv"
)

decision_df = pd.read_csv(
    PROCESSED_DIR / "decision_table.csv"
)

weekly_df = pd.read_csv(
    PROCESSED_DIR / "weekly_features.csv"
)

inventory_df = pd.read_csv(
    PROCESSED_DIR / "inventory_risk.csv"
)


# Prepare Dates

weekly_df["Week_Start"] = pd.to_datetime(
    weekly_df["Week_Start"]
)

forecast_df["Week_Start"] = pd.to_datetime(
    forecast_df["Week_Start"]
)


# Page Header

st.title("Executive Overview")

st.markdown(
    """
    **FORESIGHT — Demand & Inventory Intelligence**

    A management-level view of forecast demand, inventory position,
    operational risk, and financial exposure.
    """
)



# KPI Calculations

total_forecast = forecast_df["Forecast_Units"].sum()

reorder_skus = (
    decision_df["Business_Action"]
    .eq("Reorder Now")
    .sum()
)

revenue_exposure = (
    decision_df["Potential_Revenue_Exposure"].sum()
)

excess_inventory_value = (
    decision_df["Excess_Inventory_Value"].sum()
)

high_critical_risk = (
    inventory_df["Risk_Level"]
    .astype(str)
    .str.strip()
    .str.lower()
    .isin(["high", "critical"])
    .sum()
)


# KPI Cards

st.markdown("### Key Performance Indicators")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)


with kpi1:
    st.metric(
        "4-Week Forecast Demand",
        f"{total_forecast:,.0f} units"
    )


with kpi2:
    st.metric(
        "SKUs Requiring Reorder",
        f"{reorder_skus}"
    )


with kpi3:
    st.metric(
        "Potential Revenue Exposure",
        f"₹{revenue_exposure:,.0f}"
    )


with kpi4:
    st.metric(
        "Excess Inventory Value",
        f"₹{excess_inventory_value:,.0f}"
    )


with kpi5:
    st.metric(
        "High / Critical Risk SKUs",
        f"{high_critical_risk}"
    )



# Weekly Demand & 4-Week Forecast

st.markdown("### Weekly Demand & 4-Week Forecast")

# Historical weekly demand
historical_weekly = (
    weekly_df
    .groupby("Week_Start", as_index=False)["Weekly_Units_Sold"]
    .sum()
    .rename(
        columns={
            "Week_Start": "Week",
            "Weekly_Units_Sold": "Demand"
        }
    )
)

historical_weekly = historical_weekly.sort_values("Week")


# Forecast weekly demand
forecast_weekly = (
    forecast_df
    .groupby("Week_Start", as_index=False)["Forecast_Units"]
    .sum()
    .rename(
        columns={
            "Week_Start": "Week",
            "Forecast_Units": "Forecast"
        }
    )
)

forecast_weekly = forecast_weekly.sort_values("Week")


# Keep only the four actual forecast weeks
forecast_weekly = forecast_weekly.tail(4)



# Plotly Chart

fig = go.Figure()


fig.add_trace(
    go.Scatter(
        x=historical_weekly["Week"],
        y=historical_weekly["Demand"],
        mode="lines",
        name="Historical Demand",
        line=dict(
            color="#315C8C",
            width=2.5
        ),
        hovertemplate=(
            "<b>Historical Demand</b><br>"
            "Week: %{x|%d %b %Y}<br>"
            "Units: %{y:,.0f}"
            "<extra></extra>"
        )
    )
)


fig.add_trace(
    go.Scatter(
        x=forecast_weekly["Week"],
        y=forecast_weekly["Forecast"],
        mode="lines+markers",
        name="4-Week Forecast",
        line=dict(
            color="#9A7B4F",
            width=3
        ),
        marker=dict(
            size=8
        ),
        hovertemplate=(
            "<b>4-Week Forecast</b><br>"
            "Week: %{x|%d %b %Y}<br>"
            "Units: %{y:,.0f}"
            "<extra></extra>"
        )
    )
)


fig.update_layout(
    height=430,
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    ),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(
        color="#1F2933"
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        font=dict(
            color="#1F2933"
        )
    ),
    xaxis=dict(
        title=dict(
            text="Week",
            font=dict(
                color="#1F2933",
                size=14
            )
        ),
        tickfont=dict(
            color="#1F2933",
            size=12
        ),
        showgrid=False,
        linecolor="#D0D5DD"
    ),
    yaxis=dict(
        title=dict(
            text="Units Sold",
            font=dict(
                color="#1F2933",
                size=14
            )
        ),
        tickfont=dict(
            color="#1F2933",
            size=12
        ),
        gridcolor="#E4E1DB",
        zeroline=False,
        linecolor="#D0D5DD"
    ),
    hovermode="x unified"
)


st.plotly_chart(
    fig,
    use_container_width=True
)



# Key Business Signals

st.markdown("### Key Business Signals")

signal1, signal2, signal3 = st.columns(3)


# Signal 1
with signal1:

    st.markdown("**Demand Outlook**")

    st.write(
        f"The model forecasts approximately "
        f"**{total_forecast:,.0f} units** of demand "
        f"across the next four complete forecast weeks."
    )


# Signal 2
with signal2:

    st.markdown("**Inventory Action**")

    st.write(
        f"**{reorder_skus} SKUs** are currently classified "
        f"as **Reorder Now**, indicating that available inventory "
        f"does not sufficiently cover forecast requirements."
    )


# Signal 3
with signal3:

    st.markdown("**Financial Exposure**")

    st.write(
        f"Potential revenue exposure is approximately "
        f"**₹{revenue_exposure:,.0f}**, while excess inventory "
        f"is valued at approximately "
        f"**₹{excess_inventory_value:,.0f}**."
    )