import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path



# Load Data

BASE_DIR = Path(__file__).resolve().parent.parent

decision_path = BASE_DIR / "dashboard_data" / "decision_table.csv"
forecast_path = BASE_DIR / "dashboard_data" / "forecast_4_week.csv"
weekly_path = BASE_DIR / "dashboard_data" / "weekly_features.csv"

decision_df = pd.read_csv(decision_path)
forecast_df = pd.read_csv(forecast_path)
weekly_df = pd.read_csv(weekly_path)

weekly_df["Week_Start"] = pd.to_datetime(
    weekly_df["Week_Start"]
)

forecast_df["Week_Start"] = pd.to_datetime(
    forecast_df["Week_Start"]
)



# Page Header

st.title("SKU Analysis")

st.write(
    "Detailed SKU-level analysis combining historical demand, "
    "forecast demand, inventory position, risk, and recommended action."
)



# SKU Selection

st.markdown("### Select SKU")

sku_list = sorted(
    decision_df["SKU"].unique()
)

selected_sku = st.selectbox(
    "SKU",
    sku_list,
    label_visibility="collapsed"
)


# Selected SKU Data

sku_info = decision_df[
    decision_df["SKU"] == selected_sku
].iloc[0]

sku_forecast = (
    forecast_df[
        forecast_df["SKU"] == selected_sku
    ]
    .sort_values("Week_Start")
)

sku_history = (
    weekly_df[
        weekly_df["SKU"] == selected_sku
    ]
    .sort_values("Week_Start")
    .tail(26)
)



# SKU Summary

st.markdown(
    f"### {sku_info['Product_Name']}"
)

st.caption(
    f"{sku_info['Category']} · "
    f"{sku_info['Subcategory']} · "
    f"{selected_sku}"
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Risk",
        sku_info["Risk_Level"]
    )

with col2:
    st.metric(
        "Current Stock",
        f"{sku_info['Current_Stock']:,.0f} units"
    )

with col3:
    st.metric(
        "4-Week Forecast",
        f"{sku_forecast['Forecast_Units'].sum():,.0f} units"
    )

with col4:
    st.metric(
        "Action",
        sku_info["Recommended_Action"]
    )



# Historical Demand + Forecast

st.markdown("### Demand Trend")

fig_demand = go.Figure()

fig_demand.add_trace(
    go.Scatter(
        x=sku_history["Week_Start"],
        y=sku_history["Weekly_Units_Sold"],
        mode="lines+markers",
        name="Historical Demand",
        line=dict(
            color="#315C8C",
            width=2
        ),
        marker=dict(
            size=6
        ),
        hovertemplate=(
            "<b>%{x|%d %b %Y}</b><br>"
            "Units Sold: %{y:,.0f}"
            "<extra></extra>"
        )
    )
)

fig_demand.add_trace(
    go.Scatter(
        x=sku_forecast["Week_Start"],
        y=sku_forecast["Forecast_Units"],
        mode="lines+markers",
        name="Forecast",
        line=dict(
            color="#9A7B4F",
            width=3
        ),
        marker=dict(
            size=7
        ),
        hovertemplate=(
            "<b>%{x|%d %b %Y}</b><br>"
            "Forecast: %{y:,.0f} units"
            "<extra></extra>"
        )
    )
)

fig_demand.add_vline(
    x=sku_forecast["Week_Start"].min(),
    line_width=1,
    line_dash="dash",
    line_color="#9A7B4F"
)

fig_demand.update_layout(
    height=430,
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(color="#1F2933"),
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
            text="Week",
            font=dict(color="#1F2933", size=14)
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
            text="Units",
            font=dict(color="#1F2933", size=14)
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
    fig_demand,
    use_container_width=True
)



# Inventory Position

st.markdown("### Inventory Position")

current_stock = sku_info["Current_Stock"]
on_order = sku_info["On_Order"]
reorder_point = sku_info["Reorder_Point"]
safety_stock = sku_info["Safety_Stock"]

inventory_position = current_stock + on_order

current_coverage = sku_info[
    "Current_Stock_Coverage_Days"

]

total_coverage = sku_info[
    "Total_Stock_Coverage_Days"
]

lead_time = sku_info[
    "Lead_Time_Days"
]


left_col, right_col = st.columns(
    [1.2, 1]
)



# Numerical Analysis

with left_col:

    st.markdown("#### Inventory Metrics")

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.metric(
            "Available Inventory",
            f"{inventory_position:,.0f} units"
        )

        st.metric(
            "Current Coverage",
            f"{current_coverage:.1f} days"
        )

    with metric_col2:
        st.metric(
            "Reorder Point",
            f"{reorder_point:,.0f} units"
        )

        st.metric(
            "Total Coverage",
            f"{total_coverage:.1f} days"
        )

    st.markdown("#### Inventory Position Analysis")

    coverage_gap = total_coverage - lead_time

    st.write(
        f"**Lead Time:** {lead_time:.0f} days"
    )

    st.write(
        f"**Safety Stock:** {safety_stock:,.0f} units"
    )

    st.write(
    f"**Coverage Buffer:** {coverage_gap:.1f} days"
)

if coverage_gap >= 0:
    st.caption(
        "Total inventory coverage extends beyond the expected lead time."
    )
else:
    st.caption(
        "Total inventory coverage is below the expected lead time."
    )




# Donut Chart

with right_col:

    st.markdown("#### Inventory Composition")

    fig_inventory = go.Figure()

    fig_inventory.add_trace(
        go.Pie(
            labels=[
                "Current Stock",
                "On Order"
            ],
            values=[
                current_stock,
                on_order
            ],
            hole=0.58,
            marker=dict(
                colors=[
                    "#315C8C",
                    "#9A7B4F"
                ]
            ),
            textinfo="percent",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Units: %{value:,.0f}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )
    )

    fig_inventory.update_layout(
    height=380,
    margin=dict(
        l=10,
        r=10,
        t=10,
        b=70
    ),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(
        color="#1F2933"
    ),
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.08,
        xanchor="center",
        x=0.5,
        font=dict(
            color="#1F2933",
            size=12
        )
    ),
    annotations=[
        dict(
            text=(
                f"<b>{inventory_position:,.0f}</b>"
                "<br>Units"
            ),
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(
                size=17,
                color="#1F2933"
            )
        )
    ]
)

    st.plotly_chart(
        fig_inventory,
        use_container_width=True
    )



# SKU Interpretation

st.markdown("### SKU Interpretation")

interp_col1, interp_col2, interp_col3 = st.columns(3)

with interp_col1:
    st.metric(
        "Current Coverage",
        f"{sku_info['Current_Stock_Coverage_Days']:.1f} days"
    )

with interp_col2:
    st.metric(
        "Total Coverage",
        f"{sku_info['Total_Stock_Coverage_Days']:.1f} days"
    )

with interp_col3:
    st.metric(
        "Lead Time",
        f"{sku_info['Lead_Time_Days']:.0f} days"
    )

st.caption(
    "SKU-level decisions should be interpreted using demand "
    "forecast, inventory position, lead time, safety stock, "
    "and the modelled risk level together."
)