# pages/11_product_volume_vs_freight.py — Q11
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters, style, page_header, CVD_SEQ
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "Does a bigger product cost more to ship?",
    "Product volume vs. freight cost, for the top categories in the current filter selection."
)

d = f_delivered.dropna(subset=['product_volume_cm3', 'freight_value']).copy()
d = d[(d['product_volume_cm3'] > 0) & (d['product_volume_cm3'] < d['product_volume_cm3'].quantile(0.98))] if len(d) else d

top5 = f_items.groupby('product_category_name_english')['item_total'].sum().sort_values(ascending=False).head(5).index
d5 = d[d['product_category_name_english'].isin(top5)]

if len(d5) < 20:
    st.warning('Not enough delivered orders with product dimensions for the current filters.')
    st.stop()

k1, k2 = st.columns(2)
k1.metric('Orders plotted', f"{len(d5):,}")
k2.metric('Categories shown', f"{d5['product_category_name_english'].nunique()}")

st.divider()

# BBD CATEGORICAL: unordered distinct groups → CVD-safe qualitative sequence
fig = px.scatter(d5, x='product_volume_cm3', y='freight_value', color='product_category_name_english',
                  trendline='ols', opacity=0.35, color_discrete_sequence=CVD_SEQ,
                  labels={'product_volume_cm3': 'Product volume (cm³)', 'freight_value': 'Freight cost (R$)',
                          'product_category_name_english': 'Category'})
fig = style(fig, 'Freight scales with product volume — steepest for furniture & bed/bath/table', height=480)
st.plotly_chart(fig, theme=None, use_container_width=True)

with st.expander('📊 Show sample data'):
    st.dataframe(d5[['product_category_name_english', 'product_volume_cm3', 'freight_value']].head(200),
                 use_container_width=True)
