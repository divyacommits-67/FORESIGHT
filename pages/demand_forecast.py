import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# Paths

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "dashboard_data"

# Load Data

weekly_df = pd.read_csv(
    PROCESSED_DIR / "weekly_features.csv"
)

forecast_df = pd.read_csv(
    PROCESSED_DIR / "forecast_4_week.csv"
)

# Prepare Dates

weekly_df["Week_Start"] = pd.to_datetime(
    weekly_df["Week_Start"]
)

forecast_df["Week_Start"] = pd.to_datetime(
    forecast_df["Week_Start"]
)

# Page Header


st.title("Demand & Forecast")

st.markdown(
    """
    Analyze historical demand patterns and the model's
    four-week demand forecast.
    """
)

# Forecast Analysis

st.markdown("### Forecast Analysis")

historical_total = weekly_df["Weekly_Units_Sold"].sum()

forecast_total = forecast_df["Forecast_Units"].sum()

historical_avg_weekly = (
    weekly_df
    .groupby("Week_Start")["Weekly_Units_Sold"]
    .sum()
    .mean()
)

forecast_avg_weekly = (
    forecast_df
    .groupby("Week_Start")["Forecast_Units"]
    .sum()
    .mean()
)

forecast_change = (
    (forecast_avg_weekly - historical_avg_weekly)
    / historical_avg_weekly
    * 100
)


analysis1, analysis2, analysis3 = st.columns(3)


with analysis1:

    st.metric(
        "Historical Weekly Average",
        f"{historical_avg_weekly:,.0f} units"
    )


with analysis2:

    st.metric(
        "4-Week Forecast Average",
        f"{forecast_avg_weekly:,.0f} units"
    )


with analysis3:

    st.metric(
        "Forecast vs Historical",
        f"{forecast_change:+.1f}%"
    )



# Forecast Interpretation

st.markdown("### Forecast Interpretation")

st.write(
    f"The historical weekly demand averaged approximately "
    f"**{historical_avg_weekly:,.0f} units**, while the next four "
    f"forecast weeks average approximately "
    f"**{forecast_avg_weekly:,.0f} units**."
)

if forecast_change > 0:
    st.write(
        f"The forecast is approximately **{forecast_change:.1f}% "
        f"above** the historical weekly average."
    )
elif forecast_change < 0:
    st.write(
        f"The forecast is approximately **{abs(forecast_change):.1f}% "
        f"below** the historical weekly average."
    )
else:
    st.write(
        "The forecast is approximately in line with the historical "
        "weekly average."
    )


# Top SKUs by Forecast Demand

st.markdown("### Top SKUs by 4-Week Forecast Demand")

sku_forecast = (
    forecast_df
    .groupby("SKU", as_index=False)["Forecast_Units"]
    .sum()
    .sort_values(
        "Forecast_Units",
        ascending=False
    )
    .head(10)
    .sort_values(
        "Forecast_Units",
        ascending=True
    )
)


fig_sku = go.Figure()


fig_sku.add_trace(
    go.Bar(
        x=sku_forecast["Forecast_Units"],
        y=sku_forecast["SKU"],
        orientation="h",
        marker_color="#315C8C",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "4-Week Forecast: %{x:,.0f} units"
            "<extra></extra>"
        )
    )
)


fig_sku.update_layout(
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
    xaxis=dict(
        title=dict(
            text="Forecast Units",
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
        zeroline=False
    ),
    yaxis=dict(
        title=dict(
            text="SKU",
            font=dict(
                color="#1F2933",
                size=14
            )
        ),
        tickfont=dict(
            color="#1F2933",
            size=12
        ),
        showgrid=False
    )
)


st.plotly_chart(
    fig_sku,
    use_container_width=True
)


st.write(
    "The chart highlights the SKUs expected to account for the "
    "largest share of demand during the four-week forecast horizon. "
    "These products can be prioritized for inventory monitoring "
    "and replenishment planning."
)