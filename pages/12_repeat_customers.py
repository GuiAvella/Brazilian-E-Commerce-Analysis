# pages/12_repeat_customers.py — Q12
import streamlit as st
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters, style, page_header, GREY, BLUE
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "Are repeat customers worth more than one-time buyers?",
    "Share of the customer base that is repeat vs. one-time, and how much each group spends on average."
)

seg = (f_customers.assign(segment=lambda x: np.where(x['is_repeat'], 'Repeat customer', 'One-time customer'))
       .groupby('segment')
       .agg(n_customers=('customer_unique_id', 'count'),
            avg_spent=('total_spent', 'mean'),
            avg_review=('avg_review', 'mean'))
       .reset_index())

if seg.empty:
    st.warning('No customer data for the current filters.')
    st.stop()

seg['pct_of_customers'] = seg['n_customers'] / seg['n_customers'].sum() * 100
repeat_row = seg[seg['segment'] == 'Repeat customer']
onetime_row = seg[seg['segment'] == 'One-time customer']

k1, k2, k3 = st.columns(3)
k1.metric('Repeat customers', f"{repeat_row['pct_of_customers'].iloc[0]:.1f}%" if len(repeat_row) else '0%')
k2.metric('Avg. spend (repeat)', f"R$ {repeat_row['avg_spent'].iloc[0]:.0f}" if len(repeat_row) else '—')
k3.metric('Avg. spend (one-time)', f"R$ {onetime_row['avg_spent'].iloc[0]:.0f}" if len(onetime_row) else '—')

st.divider()

# BBD Ch.34: bar, not pie — comparing exactly two groups
fig = make_subplots(rows=1, cols=2, subplot_titles=('Share of customer base (%)', 'Avg. spend per customer (R$)'))
fig.add_trace(go.Bar(x=seg['segment'], y=seg['pct_of_customers'], marker_color=[GREY, BLUE],
                      text=seg['pct_of_customers'].round(1), textposition='outside'), row=1, col=1)
fig.add_trace(go.Bar(x=seg['segment'], y=seg['avg_spent'], marker_color=[GREY, BLUE],
                      text=seg['avg_spent'].round(0), textposition='outside'), row=1, col=2)
fig = style(fig, 'Repeat customers are rare but spend meaningfully more per head', height=440)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, theme=None, use_container_width=True)

with st.expander('📊 Show segment data'):
    st.dataframe(seg, use_container_width=True)
