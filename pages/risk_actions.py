import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path



# Load Data

BASE_DIR = Path(__file__).resolve().parent.parent

risk_path = BASE_DIR / "dashboard_data" / "decision_table.csv"

risk_df = pd.read_csv(risk_path)


# Page Header

st.title("Risk & Actions")

st.write(
    "A decision-oriented view of inventory risk, recommended "
    "business actions, and the SKUs requiring attention."
)



# Risk Metrics

risk_counts = risk_df["Risk_Level"].value_counts()

critical_count = risk_counts.get("Critical", 0)
high_count = risk_counts.get("High", 0)

reorder_count = (
    risk_df["Recommended_Action"]
    == "Reorder Now"
).sum()

markdown_count = (
    risk_df["Recommended_Action"]
    == "Markdown / Clear"
).sum()


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Critical Risk",
        critical_count
    )

with col2:
    st.metric(
        "High Risk",
        high_count
    )

with col3:
    st.metric(
        "Reorder Now",
        reorder_count
    )

with col4:
    st.metric(
        "Markdown / Clear",
        markdown_count
    )



# Risk Distribution

st.markdown("### Inventory Risk Distribution")

risk_order = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

risk_distribution = (
    risk_df["Risk_Level"]
    .value_counts()
    .reindex(risk_order, fill_value=0)
)

fig_risk = go.Figure()

fig_risk.add_trace(
    go.Bar(
        x=risk_distribution.index,
        y=risk_distribution.values,
        marker_color="#315C8C",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "SKUs: %{y}"
            "<extra></extra>"
        )
    )
)

fig_risk.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(color="#1F2933"),
    xaxis=dict(
        title=dict(
            text="Risk Level",
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
            text="Number of SKUs",
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
    fig_risk,
    use_container_width=True
)

st.write(
    "The risk distribution provides a portfolio-level view of "
    "inventory conditions. Higher-risk SKUs should be reviewed "
    "alongside their recommended business action rather than "
    "treated as identical inventory problems."
)



# Recommended Actions

st.markdown("### Recommended Actions")

action_counts = (
    risk_df["Recommended_Action"]
    .value_counts()
    .sort_values(ascending=True)
)

fig_actions = go.Figure()

fig_actions.add_trace(
    go.Bar(
        x=action_counts.values,
        y=action_counts.index,
        orientation="h",
        marker_color="#9A7B4F",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "SKUs: %{x}"
            "<extra></extra>"
        )
    )
)

fig_actions.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(color="#1F2933"),
    xaxis=dict(
        title=dict(
            text="Number of SKUs",
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
            text="Recommended Action",
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
    fig_actions,
    use_container_width=True
)

st.write(
    "Recommended actions translate the modelled inventory "
    "conditions into operational decisions such as replenishment, "
    "markdown or clearance, monitoring, and maintaining the "
    "current inventory position."
)



# Priority SKU Table

st.markdown("### Priority SKU Review")

priority_skus = (
    risk_df[
        risk_df["Recommended_Action"]
        != "Healthy"
    ]
    [
        [
            "SKU",
            "Product_Name",
            "Risk_Level",
            "Recommended_Action",
            "Risk_Score"
        ]
    ]
    .sort_values(
        ["Risk_Level", "Risk_Score"],
        ascending=[True, False]
    )
)

st.dataframe(
    priority_skus,
    use_container_width=True,
    hide_index=True
)