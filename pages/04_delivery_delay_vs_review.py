# pages/04_delivery_delay_vs_review.py — Q4
import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters, style, page_header, GREY, ORANGE, GREEN, DARKRED
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "Does a delivery that arrives late cost you review stars?",
    "Average review score, grouped by how early or late the order arrived vs. the estimate."
)

d = f_delivered.dropna(subset=['delivery_delay_days', 'review_score']).copy()
if d.empty:
    st.warning('No delivered, reviewed orders match the current filters.')
    st.stop()

d['delay_bucket'] = pd.cut(d['delivery_delay_days'], bins=[-100, -7, -1, 0, 7, 100],
                            labels=['7+ days early', '1-6 days early', 'on time', '1-7 days late', '7+ days late'])
bucket_rev = d.groupby('delay_bucket', observed=True)['review_score'].mean().reset_index()

k1, k2, k3 = st.columns(3)
on_time = bucket_rev.loc[bucket_rev['delay_bucket'] == 'on time', 'review_score']
late7 = bucket_rev.loc[bucket_rev['delay_bucket'] == '7+ days late', 'review_score']
k1.metric('On-time avg. score', f"{on_time.iloc[0]:.2f}" if len(on_time) else '—')
k2.metric('7+ days late avg. score', f"{late7.iloc[0]:.2f}" if len(late7) else '—')
k3.metric('% of orders late', f"{(d['delivery_delay_days'] > 0).mean():.1%}")

st.divider()

# BBD CVD: grey (early) → green (on time) → orange → dark red (worst) — no red/green pairing
colors = [GREEN, GREEN, GREEN, ORANGE, DARKRED]
fig = px.bar(bucket_rev, x='delay_bucket', y='review_score',
             labels={'delay_bucket': 'Delivery timing vs. estimate', 'review_score': 'Average review score'})
fig.update_traces(marker_color=colors[:len(bucket_rev)],
                   text=bucket_rev['review_score'].round(2), textposition='outside')
fig.add_hline(y=d['review_score'].mean(), line_dash='dot', line_color='#999')
fig = style(fig, 'A late delivery costs almost a full star', height=460)
fig.update_yaxes(range=[0, 5.3])
st.plotly_chart(fig, theme=None, use_container_width=True)

with st.expander('📊 Show bucket data'):
    st.dataframe(bucket_rev, use_container_width=True)
