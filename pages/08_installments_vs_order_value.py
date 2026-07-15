# pages/08_installments_vs_order_value.py — Q8
import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_data, sidebar_filters, style, page_header, CVD_SEQ
os.chdir(os.path.dirname(os.path.dirname(__file__)))

items, delivered, customers = load_data()
f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)

page_header(
    "Do more installments mean a bigger basket?",
    "Average order value by number of installments chosen, split by payment type."
)

d = f_items.dropna(subset=['main_payment_type']).query("main_payment_type != 'not_defined'")
inst = (d.groupby(['main_payment_type', 'max_installments'], as_index=False)
        .agg(avg_value=('item_total', 'mean'), n=('order_id', 'nunique'))
        .query('n >= 5 and max_installments <= 12'))

if inst.empty:
    st.warning('Not enough data for the current filters.')
    st.stop()

k1, k2 = st.columns(2)
k1.metric('Payment types shown', f"{inst['main_payment_type'].nunique()}")
k2.metric('Max installments seen', f"{int(inst['max_installments'].max())}")

st.divider()

# BBD CATEGORICAL: payment type is an unordered distinct group → CVD-safe sequence
fig = px.scatter(inst, x='max_installments', y='avg_value', color='main_payment_type', size='n',
                  color_discrete_sequence=CVD_SEQ, size_max=35,
                  labels={'max_installments': 'Number of installments', 'avg_value': 'Average order value (R$)',
                          'main_payment_type': 'Payment type'})
fig = style(fig, 'More installments track with bigger baskets — most visibly on credit cards', height=480)
st.plotly_chart(fig, use_container_width=True)

with st.expander('📊 Show installment data'):
    st.dataframe(inst.sort_values(['main_payment_type', 'max_installments']), use_container_width=True)
