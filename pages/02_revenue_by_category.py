# pages/02_revenue_by_category.py — Q2
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import *
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "Which product categories drive the most revenue — and how has that changed?",
    "Monthly revenue for the top categories in the current filter selection."
)

top_n = st.slider('Number of top categories to show', 3, 10, 6)

top_cats = (f_items.groupby('product_category_name_english')['item_total'].sum()
            .sort_values(ascending=False).head(top_n).index)

k1, k2 = st.columns(2)
k1.metric('Top category', top_cats[0] if len(top_cats) else '—')
k2.metric('Its revenue', f"R$ {f_items[f_items['product_category_name_english']==top_cats[0]]['item_total'].sum():,.0f}"
          if len(top_cats) else '—')

st.divider()

monthly_cat = (f_items[f_items['product_category_name_english'].isin(top_cats)]
               .groupby(['purchase_month', 'product_category_name_english'])['item_total']
               .sum().reset_index())

if monthly_cat.empty:
    st.warning('No data for the current filters.')
    st.stop()

# BBD CATEGORICAL: unordered distinct groups → CVD-safe qualitative sequence
fig = px.line(monthly_cat, x='purchase_month', y='item_total', color='product_category_name_english',
              color_discrete_sequence=CVD_SEQ,
              labels={'purchase_month': 'Month', 'item_total': 'Revenue (R$)', 'product_category_name_english': 'Category'})
fig.update_traces(line=dict(width=2.5))
fig = style(fig, 'Revenue trend for the top categories', height=480)
fig.update_xaxes(tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

with st.expander('📊 Show monthly totals'):
    st.dataframe(monthly_cat.sort_values(['product_category_name_english', 'purchase_month']), use_container_width=True)
