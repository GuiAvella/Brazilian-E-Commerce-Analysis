# pages/01_delivery_time_by_state.py — Q1
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import *
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "Do slower-delivery states rate their orders lower?",
    "Average delivery time vs. average review score, by customer state (bubble size = orders)."
)

state_perf = (f_delivered.groupby('customer_state', as_index=False)
              .agg(avg_delivery_days=('delivery_days', 'mean'),
                   avg_review=('review_score', 'mean'),
                   n_orders=('order_id', 'nunique'))
              .query('n_orders >= 5')
              .sort_values('avg_delivery_days'))

if state_perf.empty:
    st.warning('No delivered orders match the current filters.')
    st.stop()

k1, k2, k3 = st.columns(3)
k1.metric('States shown', f"{len(state_perf)}")
k2.metric('Fastest state', f"{state_perf.loc[state_perf['avg_delivery_days'].idxmin(), 'customer_state']}",
          f"{state_perf['avg_delivery_days'].min():.1f} days")
k3.metric('Slowest state', f"{state_perf.loc[state_perf['avg_delivery_days'].idxmax(), 'customer_state']}",
          f"{state_perf['avg_delivery_days'].max():.1f} days")

st.divider()

# BBD HIGHLIGHT: single-hue orange scale on delivery time (slower = darker) — no red/green
fig = px.scatter(state_perf, x='avg_delivery_days', y='avg_review', size='n_orders',
                  color='avg_delivery_days', color_continuous_scale=[GREY, ORANGE],
                  hover_name='customer_state', size_max=45,
                  labels={'avg_delivery_days': 'Average delivery time (days)', 'avg_review': 'Average review score (1-5)'})
fig.update_traces(marker=dict(line=dict(width=1, color='black',opacity=1)))
fig.add_hline(y=state_perf['avg_review'].mean(), line_dash='dot', line_color=BLACK, opacity=1,
              annotation_text='national average', annotation_position='top left')
fig = style(fig, 'Slower-delivery states also rate their orders lower', height=480)
fig.update_coloraxes(showscale=False)
st.plotly_chart(fig, use_container_width=True)

with st.expander('📊 Show state-level data'):
    st.dataframe(state_perf.sort_values('avg_delivery_days'), use_container_width=True)
