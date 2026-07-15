"""
Brazil's Marketplace in Motion — Olist E-Commerce Dashboard
=============================================================
Run with: streamlit run app.py   (from the project root)

Every one of the 12 analytical questions from the notebook gets its own
page here, in the same order. One shared sidebar (see utils.py) carries
your filters across all of them.
"""

import streamlit as st

st.set_page_config(page_title="Olist Brazil · E-Commerce Dashboard", page_icon="🇧🇷",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; padding-bottom: 0; }
[data-testid='metric-container'] {
    background: #F8F9FA; border: 1px solid #E9ECEF;
    padding: 1rem; border-radius: 8px;
}
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

pg = st.navigation([
    st.Page("pages/01_delivery_time_by_state.py",
            title="Q1 · Do slower-delivery states rate lower?",         icon="🚚"),
    st.Page("pages/02_revenue_by_category.py",
            title="Q2 · Which categories drive revenue growth?",       icon="📈"),
    st.Page("pages/03_freight_ratio_by_category.py",
            title="Q3 · What's costliest to ship, relative to price?", icon="📦"),
    st.Page("pages/04_delivery_delay_vs_review.py",
            title="Q4 · Does a late delivery cost you stars?",         icon="⏰"),
    st.Page("pages/05_state_value_installments.py",
            title="Q5 · Who spends most, and how do they pay?",        icon="💳"),
    st.Page("pages/06_price_tier_vs_review.py",
            title="Q6 · Does a higher price mean happier customers?",  icon="🏷️"),
    st.Page("pages/07_weekly_order_rhythm.py",
            title="Q7 · What's the weekly shopping rhythm?",           icon="📅"),
    st.Page("pages/08_installments_vs_order_value.py",
            title="Q8 · Do more installments mean bigger baskets?",    icon="🧾"),
    st.Page("pages/09_seller_revenue_concentration.py",
            title="Q9 · How concentrated is seller revenue?",          icon="🏪"),
    st.Page("pages/10_cross_state_shipping.py",
            title="Q10 · How often do orders ship cross-state?",       icon="🗺️"),
    st.Page("pages/11_product_volume_vs_freight.py",
            title="Q11 · Does bigger mean pricier to ship?",           icon="📐"),
    st.Page("pages/12_repeat_customers.py",
            title="Q12 · Are repeat customers worth more?",            icon="🔁"),
])
pg.run()
