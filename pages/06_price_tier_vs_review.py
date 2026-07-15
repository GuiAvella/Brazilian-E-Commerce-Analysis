# pages/06_price_tier_vs_review.py — Q6
import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters, style, page_header, CVD_SEQ
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "Does paying more buy a happier customer?",
    "Average review score by price quartile, within each of the top-selling categories."
)

d = f_delivered.dropna(subset=['review_score', 'price']).copy()
if len(d) < 20:
    st.warning('Not enough reviewed orders for the current filters.')
    st.stop()

d['price_tier'] = pd.qcut(d['price'], 4, labels=['Q1 (cheapest)', 'Q2', 'Q3', 'Q4 (priciest)'], duplicates='drop')
top6 = f_items.groupby('product_category_name_english')['item_total'].sum().sort_values(ascending=False).head(6).index
d6 = d[d['product_category_name_english'].isin(top6)]

if d6.empty:
    st.warning('No overlap between top categories and reviewed orders for the current filters.')
    st.stop()

overall_by_tier = d.groupby('price_tier', observed=True)['review_score'].mean()
k1, k2 = st.columns(2)
k1.metric('Cheapest quartile avg. score', f"{overall_by_tier.iloc[0]:.2f}")
k2.metric('Priciest quartile avg. score', f"{overall_by_tier.iloc[-1]:.2f}",
          f"{overall_by_tier.iloc[-1]-overall_by_tier.iloc[0]:+.2f} vs cheapest")

st.divider()

pivot = d6.groupby(['product_category_name_english', 'price_tier'], observed=True)['review_score'].mean().reset_index()

# BBD CATEGORICAL: price tiers are ordered groups within each category → CVD-safe sequence
fig = px.bar(pivot, x='product_category_name_english', y='review_score', color='price_tier', barmode='group',
             color_discrete_sequence=CVD_SEQ,
             labels={'product_category_name_english': '', 'review_score': 'Average review score', 'price_tier': 'Price tier'})
fig = style(fig, "Higher price tiers don't buy higher satisfaction", height=480)
fig.update_yaxes(range=[max(0, pivot['review_score'].min()-0.3), 5])
fig.update_xaxes(tickangle=-20)
st.plotly_chart(fig, use_container_width=True)

with st.expander('📊 Show pivot data'):
    st.dataframe(pivot, use_container_width=True)
