# pages/07_weekly_order_rhythm.py — Q7
import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import *
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "What's the weekly rhythm of order placement, and has it shifted over time?",
    "Number of orders placed by day of week, compared across purchase years."
)

dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
years_present = sorted(f_items['purchase_year'].dropna().unique().tolist())

weekly = (f_items.groupby(['purchase_year', 'purchase_dow'])['order_id'].nunique().reset_index())
weekly['purchase_dow'] = pd.Categorical(weekly['purchase_dow'], categories=dow_order, ordered=True)
weekly = weekly.sort_values('purchase_dow')

if weekly.empty:
    st.warning('No data for the current filters.')
    st.stop()

busiest = weekly.loc[weekly['order_id'].idxmax()]
k1, k2 = st.columns(2)
k1.metric('Busiest day overall', str(busiest['purchase_dow']))
k2.metric('Years compared', f"{len(years_present)}")

st.divider()

# BBD CATEGORICAL: year is a small ordered set of lines → grey (older) vs blue (newest)
palette = CVD_SEQ[:max(len(years_present), 1)]
fig = px.line(weekly, x='purchase_dow', y='order_id', color='purchase_year',
              color_discrete_sequence=palette, markers=True,
              labels={'purchase_dow': 'Day of week', 'order_id': 'Number of orders', 'purchase_year': 'Year'})
fig.update_traces(line=dict(width=2.5), marker=dict(size=8))
fig = style(fig, 'Weekday order volume grows faster than weekends year over year', height=460)
st.plotly_chart(fig, theme=None, use_container_width=True)

with st.expander('📊 Show weekly data'):
    st.dataframe(weekly, use_container_width=True)
