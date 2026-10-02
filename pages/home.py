import streamlit as st

# Hero Section

st.title("FORESIGHT")

st.subheader("Demand & Inventory Intelligence")

st.write(
    "FORESIGHT transforms demand, inventory, forecasting, and risk "
    "data into clear business insights that support smarter "
    "inventory planning and operational decisions."
)


# Platform Overview

st.markdown("### What FORESIGHT Provides")

st.caption(
    "A unified view of demand, inventory health, risk, and financial impact."
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### Executive Insights")
    st.write(
        "High-level performance indicators provide a quick view "
        "of operational health and business exposure."
    )

with col2:
    st.markdown("### Demand Forecasting")
    st.write(
        "Historical demand patterns and forecasts support "
        "forward-looking inventory planning."
    )

with col3:
    st.markdown("### Inventory Risk")
    st.write(
        "Inventory levels, coverage, and risk indicators help "
        "identify products requiring attention."
    )

with col4:
    st.markdown("### Financial Impact")
    st.write(
        "Modelled financial exposure and inventory investment "
        "provide context for operational decisions."
    )



# How FORESIGHT Works

st.markdown("---")

st.markdown("### How FORESIGHT Works")

st.caption(
    "From raw business data to practical inventory decisions."
)

step1, step2, step3, step4, step5, step6 = st.columns(6)

with step1:
    st.markdown("### 📥")
    st.markdown("**01 · Data**")
    st.caption("Sales, SKU, calendar, and inventory data.")

with step2:
    st.markdown("### 🔎")
    st.markdown("**02 · Analysis**")
    st.caption("Identify demand and inventory patterns.")

with step3:
    st.markdown("### 📈")
    st.markdown("**03 · Forecast**")
    st.caption("Estimate upcoming SKU-level demand.")

with step4:
    st.markdown("### ⚠️")
    st.markdown("**04 · Risk**")
    st.caption("Detect stockout and overstock signals.")

with step5:
    st.markdown("### 💰")
    st.markdown("**05 · Impact**")
    st.caption("Quantify potential financial exposure.")

with step6:
    st.markdown("### 🎯")
    st.markdown("**06 · Action**")
    st.caption("Support replenishment and inventory decisions.")



# Explore FORESIGHT

st.markdown("---")

st.markdown("### Explore FORESIGHT")

st.write(
    "Use the sidebar to move from high-level business insights "
    "to detailed demand, inventory, risk, financial, and SKU analysis."
)

explore1, explore2, explore3 = st.columns(3)

with explore1:
    st.markdown("### 📊 Executive Overview")
    st.caption(
        "Monitor key business indicators and the overall demand outlook."
    )

with explore2:
    st.markdown("### 📦 Inventory & Risk")
    st.caption(
        "Understand inventory health, risk levels, and recommended actions."
    )

with explore3:
    st.markdown("### 💰 Financial & SKU Analysis")
    st.caption(
        "Explore financial exposure and detailed SKU-level performance."
    )