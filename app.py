import streamlit as st

st.set_page_config(
    page_title="FORESIGHT",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Sidebar Navigation

with st.sidebar:

    st.markdown(
        """
        <div style="padding: 10px 0 25px 0;">
            <h2 style="margin: 0;">FORESIGHT</h2>
            <p style="margin: 4px 0 0 0; color: #667085;">
                Demand & Inventory Intelligence
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    page = st.navigation(
        [
            st.Page(
                "pages/home.py",
                title="Home",
                icon=":material/home:"
            ),
            
            st.Page(
                "pages/executive_overview.py",
                title="Executive Overview",
                icon=":material/dashboard:"
            ),
            st.Page(
                "pages/demand_forecast.py",
                title="Demand & Forecast",
                icon=":material/analytics:"
            ),
            st.Page(
                "pages/inventory_health.py",
                title="Inventory Health",
                icon=":material/inventory_2:"
            ),
            st.Page(
                "pages/risk_actions.py",
                title="Risk & Actions",
                icon=":material/warning:"
            ),
            st.Page(
                "pages/financial_impact.py",
                title="Financial Impact",
                icon=":material/attach_money:"
            ),
            st.Page(
                "pages/sku_analysis.py",
                title="SKU Analysis",
                icon=":material/search:"
            ),
        ]
    )
page.run()