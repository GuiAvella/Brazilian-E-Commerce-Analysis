# pages/03_freight_ratio_by_category.py — Q3
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters, style, page_header, GREY, BLUE
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "Which categories cost the most to ship, relative to what they're worth?",
    "Median freight cost as a share of item price, by product category (min. 20 orders)."
)

cat_freight = (f_delivered.groupby('product_category_name_english')
               .agg(median_ratio=('freight_ratio', 'median'), n=('order_id', 'count'))
               .query('n >= 20').sort_values('median_ratio', ascending=False).head(12).reset_index())

if cat_freight.empty:
    st.warning('Not enough delivered orders per category for the current filters.')
    st.stop()

k1, k2 = st.columns(2)
k1.metric('Worst freight ratio', cat_freight.iloc[0]['product_category_name_english'],
          f"{cat_freight.iloc[0]['median_ratio']:.0%} of price")
k2.metric('Best freight ratio', cat_freight.iloc[-1]['product_category_name_english'],
          f"{cat_freight.iloc[-1]['median_ratio']:.0%} of price")

st.divider()

# BBD HIGHLIGHT: single blue sequential scale — one dominant colour
fig = px.bar(cat_freight.sort_values('median_ratio'), x='median_ratio', y='product_category_name_english',
             orientation='h', color='median_ratio', color_continuous_scale=[GREY, BLUE],
             labels={'median_ratio': 'Median freight ÷ price', 'product_category_name_english': ''})
fig = style(fig, 'Bulky, low-value categories carry the heaviest relative freight cost', height=500)
fig.update_coloraxes(showscale=False)
fig.update_xaxes(tickformat='.0%')
st.plotly_chart(fig, use_container_width=True)

with st.expander('📊 Show category data'):
    st.dataframe(cat_freight, use_container_width=True)
