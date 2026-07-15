# pages/05_state_value_installments.py — Q5
import streamlit as st
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters, style, page_header, BLUE, ORANGE
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "Which states spend the most per order, and how do they pay for it?",
    "Average order value vs. average number of installments chosen, by state (top 15 by value)."
)

state_value = (f_items.groupby('customer_state', as_index=False)
               .agg(avg_order_value=('item_total', 'mean'),
                    avg_installments=('max_installments', 'mean'),
                    n=('order_id', 'nunique'))
               .query('n >= 5').sort_values('avg_order_value', ascending=False).head(15))

if state_value.empty:
    st.warning('No data for the current filters.')
    st.stop()

k1, k2 = st.columns(2)
k1.metric('Highest avg. order value', state_value.iloc[0]['customer_state'],
          f"R$ {state_value.iloc[0]['avg_order_value']:.0f}")
k2.metric('Its avg. installments', f"{state_value.iloc[0]['avg_installments']:.1f}")

st.divider()

# BBD HIGHLIGHT: blue bars (primary metric) + orange line (secondary) — no red/green
fig = go.Figure()
fig.add_bar(x=state_value['customer_state'], y=state_value['avg_order_value'], name='Avg order value (R$)',
            marker_color=BLUE, yaxis='y')
fig.add_scatter(x=state_value['customer_state'], y=state_value['avg_installments'], name='Avg installments',
                 mode='lines+markers', marker=dict(color=ORANGE, size=8), line=dict(width=2), yaxis='y2')
fig.update_layout(
    yaxis=dict(title='Avg order value (R$)'),
    yaxis2=dict(title='Avg installments chosen', overlaying='y', side='right', showgrid=False),
    legend=dict(orientation='h', y=1.12, x=0.02))
fig = style(fig, 'Northern states spend more per order — and finance it in more installments', height=480)
st.plotly_chart(fig, use_container_width=True)

with st.expander('📊 Show state data'):
    st.dataframe(state_value, use_container_width=True)
