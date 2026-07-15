# pages/09_seller_revenue_concentration.py — Q9
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters, style, page_header, BLUE, GREY, ORANGE
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "How concentrated is revenue across sellers?",
    "Cumulative share of revenue captured as sellers are ranked from highest- to lowest-earning."
)

seller_rev = f_items.groupby('seller_id')['item_total'].sum().sort_values(ascending=False).reset_index()
if seller_rev.empty:
    st.warning('No data for the current filters.')
    st.stop()

seller_rev['cum_share'] = seller_rev['item_total'].cumsum() / seller_rev['item_total'].sum()
seller_rev['seller_rank_pct'] = (np.arange(1, len(seller_rev) + 1) / len(seller_rev)) * 100
top20_share = seller_rev.loc[seller_rev['seller_rank_pct'] <= 20, 'item_total'].sum() / seller_rev['item_total'].sum()

k1, k2 = st.columns(2)
k1.metric('Sellers', f"{len(seller_rev):,}")
k2.metric('Revenue from top 20% of sellers', f"{top20_share:.0%}")

st.divider()

# BBD HIGHLIGHT: one blue curve vs a grey equality line — single dominant colour
fig = go.Figure()
fig.add_scatter(x=seller_rev['seller_rank_pct'], y=seller_rev['cum_share'] * 100, mode='lines',
                 line=dict(color=BLUE, width=3), fill='tozeroy', fillcolor='rgba(46,117,182,0.12)')
fig.add_scatter(x=[0, 100], y=[0, 100], mode='lines', line=dict(color=GREY, width=1.5, dash='dot'))
fig.add_annotation(x=20, y=top20_share * 100, text=f"top 20% of sellers = {top20_share:.0%} of revenue",
                    showarrow=True, arrowhead=2, ax=60, ay=-40, font=dict(color=ORANGE))
fig = style(fig, 'A small slice of sellers accounts for most marketplace revenue', height=480)
fig.update_xaxes(title='Sellers ranked by revenue (cumulative %)')
fig.update_yaxes(title='Cumulative share of revenue (%)')
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

with st.expander('📊 Show top sellers'):
    st.dataframe(seller_rev.head(20), use_container_width=True)
