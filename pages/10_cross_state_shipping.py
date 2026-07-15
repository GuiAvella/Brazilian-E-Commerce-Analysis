# pages/10_cross_state_shipping.py — Q10
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters, style, page_header, GREEN, GREY
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "How often does an order ship in from another state?",
    "Share of orders where the seller's state differs from the customer's state."
)

cross = (f_items.groupby('customer_state', as_index=False)
         .agg(pct_cross_state=('cross_state_shipment', 'mean'), n=('order_id', 'nunique'))
         .query('n >= 5').sort_values('pct_cross_state', ascending=False))

if cross.empty:
    st.warning('No data for the current filters.')
    st.stop()

cross['pct_cross_state'] *= 100
k1, k2 = st.columns(2)
k1.metric('National average', f"{cross['pct_cross_state'].mean():.0f}%")
k2.metric('Highest state', cross.iloc[0]['customer_state'], f"{cross.iloc[0]['pct_cross_state']:.0f}%")

st.divider()

# BBD HIGHLIGHT: green→grey sequential scale on the metric itself — no red/green pairing
fig = px.bar(cross, x='customer_state', y='pct_cross_state', color='pct_cross_state',
             color_continuous_scale=[GREEN, GREY],
             labels={'customer_state': 'Customer state', 'pct_cross_state': '% of orders shipped from another state'})
fig.add_hline(y=cross['pct_cross_state'].mean(), line_dash='dot', line_color='#666',
              annotation_text='national average', annotation_position='top right')
fig = style(fig, 'Outside the São Paulo–Rio–Minas core, most orders ship in from elsewhere', height=480)
fig.update_coloraxes(showscale=False)
st.plotly_chart(fig, use_container_width=True)

with st.expander('📊 Show state data'):
    st.dataframe(cross, use_container_width=True)
