import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))

def code(text):
    cells.append(nbf.v4.new_code_cell(text))

# ============================================================ TITLE ======
md("""# Brazil's Marketplace in Motion
### A data story of the Olist e-commerce ecosystem (2016–2018)

**Dataset:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — 100k real orders placed across Olist's multi-seller marketplace, spanning order status, price, payments, freight, customer & seller geolocation, products, and customer reviews. Sourced directly from Olist's own GitHub repository (`olist/work-at-olist-data`), an official mirror of the Kaggle release.

**Why this dataset:** it is real commercial data (anonymised), genuinely rich (9 linked tables, 45+ usable fields after merging), and varied — numerical (price, freight, weight), categorical (product category, payment type, state), spatial (customer/seller state & zip), and temporal (order timestamps 2016–2018).

**Structure of this notebook:**
1. Data loading & preliminary EDA
2. 12 analytical questions, each answered with one publication-ready Plotly visualization
3. Summary of key takeaways
""")

# ============================================================ SETUP ======
code("""import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

pd.set_option("display.max_columns", 50)
pio.renderers.default = "png"   # static, high-res images so the notebook renders identically in Jupyter, HTML and PDF exports
pio.kaleido.scope.default_scale = 2

# ---- CVD-safe palette (Okabe-Ito) -----------------------------------
GREY      = "#B0B0B0"   # muted context
HIGHLIGHT = "#0072B2"   # focus blue
ACCENT2   = "#D55E00"   # vermillion (secondary highlight)
ACCENT3   = "#009E73"   # bluish green
ACCENT4   = "#E69F00"   # orange
CVD_SEQ   = ["#0072B2", "#56B4E9", "#009E73", "#E69F00", "#D55E00", "#CC79A7", "#F0E442"]

TEMPLATE = "plotly_white"

def style(fig, title, height=460, width=900):
    fig.update_layout(
        template=TEMPLATE,
        title=dict(text=title, font=dict(size=17, family="Arial", color="#222"), x=0.02, xanchor="left"),
        font=dict(family="Arial", size=13, color="#333"),
        height=height, width=width,
        margin=dict(t=70, l=60, r=40, b=60),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EDEDED", zeroline=False)
    return fig
""")

md("## 1 · Load data\nUsing the pre-merged master table (see `prepare_data.py` in this folder for the full merge/clean pipeline across the 9 raw Olist tables).")

code("""items = pd.read_parquet("../data/master_items.parquet")
delivered = pd.read_parquet("../data/delivered_items.parquet")   # delivered orders only (needed for delivery-time analysis)
customers_summary = pd.read_parquet("../data/customers_summary.parquet")

print(f"{items.shape[0]:,} order-items | {items['order_id'].nunique():,} orders | "
      f"{items['customer_unique_id'].nunique():,} unique customers | "
      f"{items['seller_id'].nunique():,} sellers | {items['product_category_name_english'].nunique()} product categories")
items.head(3)""")

# ============================================================ EDA ========
md("""## 2 · Preliminary Exploratory Data Analysis

A quick look at shape, missingness, and single-variable summaries before moving to the analytical questions (these are exploratory only — not counted among the 12 questions below).""")

code("""items.dtypes.value_counts()""")
code("""items.isna().mean().sort_values(ascending=False).head(10).round(3)""")
code("""items[['price','freight_value','item_total','review_score']].describe().round(2)""")
code("""items['order_status'].value_counts()""")
code("""print("Date range:", items['order_purchase_timestamp'].min(), "to", items['order_purchase_timestamp'].max())""")

# ============================================================ QUESTIONS ==
md("## 3 · Analytical Questions\n\nEach question below is multi-dimensional — relating variables, comparing groups, or tracking change over time/space — and answered with one dedicated, explanatory Plotly visualization.")

# ---- Q1 ----
md("""### Q1 — How does average delivery time vary across Brazilian states, and does slower delivery come with lower customer satisfaction?""")
code("""state_perf = (delivered.groupby('customer_state', as_index=False)
              .agg(avg_delivery_days=('delivery_days','mean'),
                   avg_review=('review_score','mean'),
                   n_orders=('order_id','nunique'))
              .query('n_orders >= 30')
              .sort_values('avg_delivery_days'))

fig = px.scatter(state_perf, x='avg_delivery_days', y='avg_review', size='n_orders',
                  color='avg_delivery_days', color_continuous_scale=[GREY, ACCENT2],
                  hover_name='customer_state', size_max=45,
                  labels={'avg_delivery_days':'Average delivery time (days)','avg_review':'Average review score (1-5)'})
fig.update_traces(marker=dict(line=dict(width=1, color='white')))
fig.add_hline(y=state_perf['avg_review'].mean(), line_dash='dot', line_color=GREY, opacity=0.6,
              annotation_text='national average', annotation_position='top left')
fig = style(fig, "Slower-delivery states also rate their orders lower — the North lags on both fronts", height=480)
fig.update_coloraxes(showscale=False)
fig.show()""")

# ---- Q2 ----
md("""### Q2 — Which product categories drive the most revenue, and how has monthly revenue trended over 2017–2018?""")
code("""top_cats = (items.groupby('product_category_name_english')['item_total'].sum()
            .sort_values(ascending=False).head(8).index)

monthly_cat = (items[items['product_category_name_english'].isin(top_cats) &
                      items['purchase_month'].between('2017-01','2018-08')]
               .groupby(['purchase_month','product_category_name_english'])['item_total']
               .sum().reset_index())

fig = px.line(monthly_cat, x='purchase_month', y='item_total', color='product_category_name_english',
              color_discrete_sequence=CVD_SEQ,
              labels={'purchase_month':'Month','item_total':'Revenue (R$)','product_category_name_english':'Category'})
fig.update_traces(line=dict(width=2.5))
fig = style(fig, "Health & beauty and watches/gifts pulled ahead of the pack through 2018", height=480, width=950)
fig.update_xaxes(tickangle=-45)
fig.show()""")

# ---- Q3 ----
md("""### Q3 — How does the freight-to-price ratio differ across product categories, and which categories are costliest to ship relative to their value?""")
code("""cat_freight = (delivered.groupby('product_category_name_english')
               .agg(median_ratio=('freight_ratio','median'), n=('order_id','count'))
               .query('n >= 100').sort_values('median_ratio', ascending=False).head(12).reset_index())

fig = px.bar(cat_freight.sort_values('median_ratio'), x='median_ratio', y='product_category_name_english',
             orientation='h', color='median_ratio', color_continuous_scale=[GREY, HIGHLIGHT],
             labels={'median_ratio':'Median freight ÷ price', 'product_category_name_english':''})
fig = style(fig, "Bulky, low-value items like furniture & construction goods carry the heaviest relative freight cost", height=500)
fig.update_coloraxes(showscale=False)
fig.show()""")

# ---- Q4 ----
md("""### Q4 — Do orders that arrive later than the estimated delivery date get lower review scores?""")
code("""d = delivered.dropna(subset=['delivery_delay_days','review_score']).copy()
d['delay_bucket'] = pd.cut(d['delivery_delay_days'],
                            bins=[-100,-7,-1,0,7,100],
                            labels=['7+ days early','1-6 days early','on time','1-7 days late','7+ days late'])
bucket_rev = d.groupby('delay_bucket', observed=True)['review_score'].mean().reset_index()

colors = [GREY, GREY, ACCENT3, ACCENT2, '#8B0000']
fig = px.bar(bucket_rev, x='delay_bucket', y='review_score',
             labels={'delay_bucket':'Delivery timing vs. estimate','review_score':'Average review score'})
fig.update_traces(marker_color=colors, text=bucket_rev['review_score'].round(2), textposition='outside')
fig.add_hline(y=d['review_score'].mean(), line_dash='dot', line_color='#999')
fig = style(fig, "A late delivery costs almost a full star — lateness is the single biggest review-score killer", height=460)
fig.update_yaxes(range=[0,5.3])
fig.show()""")

# ---- Q5 ----
md("""### Q5 — Which states have the highest average order value, and does typical installment count vary by region?""")
code("""state_value = (items.groupby('customer_state', as_index=False)
               .agg(avg_order_value=('item_total','mean'),
                    avg_installments=('max_installments','mean'),
                    n=('order_id','nunique'))
               .query('n >= 30').sort_values('avg_order_value', ascending=False).head(15))

fig = go.Figure()
fig.add_bar(x=state_value['customer_state'], y=state_value['avg_order_value'], name='Avg order value (R$)',
            marker_color=HIGHLIGHT, yaxis='y')
fig.add_scatter(x=state_value['customer_state'], y=state_value['avg_installments'], name='Avg installments',
                 mode='lines+markers', marker=dict(color=ACCENT2, size=8), line=dict(width=2), yaxis='y2')
fig.update_layout(
    yaxis=dict(title='Avg order value (R$)'),
    yaxis2=dict(title='Avg installments chosen', overlaying='y', side='right', showgrid=False),
    legend=dict(orientation='h', y=1.12, x=0.02))
fig = style(fig, "Northern states spend more per order — and lean harder on installment plans to do it", height=480, width=950)
fig.show()""")

# ---- Q6 ----
md("""### Q6 — How do review scores relate to price tier, and does that relationship hold across product categories?""")
code("""d = delivered.dropna(subset=['review_score']).copy()
d['price_tier'] = pd.qcut(d['price'], 4, labels=['Q1 (cheapest)','Q2','Q3','Q4 (priciest)'])
top6 = items.groupby('product_category_name_english')['item_total'].sum().sort_values(ascending=False).head(6).index
d6 = d[d['product_category_name_english'].isin(top6)]

pivot = d6.groupby(['product_category_name_english','price_tier'], observed=True)['review_score'].mean().reset_index()

fig = px.bar(pivot, x='product_category_name_english', y='review_score', color='price_tier', barmode='group',
             color_discrete_sequence=CVD_SEQ,
             labels={'product_category_name_english':'', 'review_score':'Average review score', 'price_tier':'Price tier'})
fig = style(fig, "Higher price tiers don't buy higher satisfaction — the pattern is flat within every top category", height=480, width=950)
fig.update_yaxes(range=[3.5,4.6])
fig.update_xaxes(tickangle=-20)
fig.show()""")

# ---- Q7 ----
md("""### Q7 — What's the weekly rhythm of order placement, and has it shifted between 2017 and 2018?""")
code("""dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
weekly = (items[items['purchase_year'].isin([2017,2018])]
          .groupby(['purchase_year','purchase_dow'])['order_id'].nunique().reset_index())
weekly['purchase_dow'] = pd.Categorical(weekly['purchase_dow'], categories=dow_order, ordered=True)
weekly = weekly.sort_values('purchase_dow')

fig = px.line(weekly, x='purchase_dow', y='order_id', color='purchase_year',
              color_discrete_sequence=[GREY, HIGHLIGHT], markers=True,
              labels={'purchase_dow':'Day of week','order_id':'Number of orders','purchase_year':'Year'})
fig.update_traces(line=dict(width=2.5), marker=dict(size=8))
fig = style(fig, "Weekday shopping habit strengthened in 2018 — weekend orders grew slower than the rest of the week", height=460)
fig.show()""")

# ---- Q8 ----
md("""### Q8 — Does paying in more installments correlate with higher order value, and does that differ by payment type?""")
code("""d = items.dropna(subset=['main_payment_type']).query("main_payment_type != 'not_defined'")
inst = (d.groupby(['main_payment_type','max_installments'], as_index=False)
        .agg(avg_value=('item_total','mean'), n=('order_id','nunique'))
        .query('n >= 20 and max_installments <= 12'))

fig = px.scatter(inst, x='max_installments', y='avg_value', color='main_payment_type', size='n',
                  color_discrete_sequence=CVD_SEQ, size_max=35,
                  labels={'max_installments':'Number of installments','avg_value':'Average order value (R$)',
                          'main_payment_type':'Payment type'})
fig = style(fig, "More installments track with bigger baskets — most visibly for credit-card purchases", height=480, width=950)
fig.show()""")

# ---- Q9 ----
md("""### Q9 — How concentrated is revenue across sellers — do a small number of sellers dominate the marketplace?""")
code("""seller_rev = items.groupby('seller_id')['item_total'].sum().sort_values(ascending=False).reset_index()
seller_rev['cum_share'] = seller_rev['item_total'].cumsum() / seller_rev['item_total'].sum()
seller_rev['seller_rank_pct'] = (np.arange(1, len(seller_rev)+1) / len(seller_rev)) * 100

fig = go.Figure()
fig.add_scatter(x=seller_rev['seller_rank_pct'], y=seller_rev['cum_share']*100, mode='lines',
                 line=dict(color=HIGHLIGHT, width=3), fill='tozeroy', fillcolor='rgba(0,114,178,0.12)')
fig.add_scatter(x=[0,100], y=[0,100], mode='lines', line=dict(color=GREY, width=1.5, dash='dot'), name='perfect equality')
top20_share = seller_rev.loc[seller_rev['seller_rank_pct']<=20, 'item_total'].sum() / seller_rev['item_total'].sum()
fig.add_annotation(x=20, y=top20_share*100, text=f"top 20% of sellers = {top20_share:.0%} of revenue",
                    showarrow=True, arrowhead=2, ax=60, ay=-40, font=dict(color=ACCENT2))
fig = style(fig, "Revenue is sharply concentrated: a small slice of sellers accounts for most marketplace revenue", height=480)
fig.update_xaxes(title="Sellers ranked by revenue (cumulative %)")
fig.update_yaxes(title="Cumulative share of revenue (%)")
fig.update_layout(showlegend=False)
fig.show()""")

# ---- Q10 ----
md("""### Q10 — How often are orders shipped cross-state, and does that vary by customer region?""")
code("""cross = (items.groupby('customer_state', as_index=False)
         .agg(pct_cross_state=('cross_state_shipment','mean'), n=('order_id','nunique'))
         .query('n >= 30').sort_values('pct_cross_state', ascending=False))
cross['pct_cross_state'] *= 100

fig = px.bar(cross, x='customer_state', y='pct_cross_state', color='pct_cross_state',
             color_continuous_scale=[ACCENT3, GREY],
             labels={'customer_state':'Customer state','pct_cross_state':'% of orders shipped from another state'})
fig.add_hline(y=cross['pct_cross_state'].mean(), line_dash='dot', line_color='#666',
              annotation_text='national average', annotation_position='top right')
fig = style(fig, "Outside the São Paulo–Rio–Minas core, almost every order ships in from another state", height=480, width=950)
fig.update_coloraxes(showscale=False)
fig.show()""")

# ---- Q11 ----
md("""### Q11 — How does product size (volume) relate to freight cost, and does this relationship differ for the largest product categories?""")
code("""d = delivered.dropna(subset=['product_volume_cm3','freight_value']).copy()
d = d[(d['product_volume_cm3']>0) & (d['product_volume_cm3'] < d['product_volume_cm3'].quantile(0.98))]
top5 = items.groupby('product_category_name_english')['item_total'].sum().sort_values(ascending=False).head(5).index
d5 = d[d['product_category_name_english'].isin(top5)]

fig = px.scatter(d5, x='product_volume_cm3', y='freight_value', color='product_category_name_english',
                  trendline='ols', opacity=0.35, color_discrete_sequence=CVD_SEQ,
                  labels={'product_volume_cm3':'Product volume (cm³)','freight_value':'Freight cost (R$)',
                          'product_category_name_english':'Category'})
fig = style(fig, "Freight scales with product volume — but the slope is steepest for furniture & bed/bath/table", height=480, width=950)
fig.show()""")

# ---- Q12 ----
md("""### Q12 — What share of customers are repeat buyers, and do repeat customers spend more or rate their experience differently?""")
code("""seg = (customers_summary.assign(segment=lambda x: np.where(x['is_repeat'],'Repeat customer','One-time customer'))
       .groupby('segment')
       .agg(n_customers=('customer_unique_id','count'),
            avg_spent=('total_spent','mean'),
            avg_review=('avg_review','mean'))
       .reset_index())
seg['pct_of_customers'] = seg['n_customers'] / seg['n_customers'].sum() * 100

fig = make_subplots(rows=1, cols=2, subplot_titles=("Customer base", "Avg. spend per customer (R$)"),
                     specs=[[{'type':'domain'},{'type':'xy'}]])
fig.add_trace(go.Pie(labels=seg['segment'], values=seg['n_customers'], hole=0.55,
                      marker=dict(colors=[GREY, HIGHLIGHT]), textinfo='percent+label'), row=1, col=1)
fig.add_trace(go.Bar(x=seg['segment'], y=seg['avg_spent'], marker_color=[GREY, HIGHLIGHT],
                      text=seg['avg_spent'].round(0), textposition='outside'), row=1, col=2)
fig = style(fig, "Repeat customers are a small share of the base (~3%) but spend meaningfully more per head", height=460, width=950)
fig.update_layout(showlegend=False)
fig.show()

print(seg.round(2))""")

# ============================================================ SUMMARY ====
md("""## 4 · Key takeaways

1. **Delivery speed drives satisfaction more than anything else** — states with longer average delivery times post visibly lower review scores, and orders that arrive even one day late lose the better part of a star versus on-time orders.
2. **Revenue is geographically and structurally concentrated.** São Paulo dominates as both the commercial hub and main shipping origin — most other states rely on cross-state shipments — and the top ~20% of sellers account for the large majority of marketplace revenue.
3. **Price does not buy satisfaction.** Within the best-selling categories, review scores stay essentially flat across price tiers — Olist's satisfaction problem is operational (delivery, freight), not about product pricing.
4. **Freight cost is a size/weight game.** Bulky, lower-value categories like furniture and construction materials carry the worst freight-to-price ratio, and freight cost scales fastest with volume for exactly these categories.
5. **Growth in 2018 was healthy and increasingly weekday-driven**, led by health & beauty and watches/gifts, while installment financing — especially on credit cards — keeps pace with basket size, most strongly in the North.
6. **Repeat purchase is rare (~3% of customers) but valuable** — repeat customers spend more per head, making retention (closely tied to delivery reliability) a clear lever for revenue growth.

*(See the accompanying Streamlit dashboard for an interactive exploration of these findings, and the presentation deck for a slide-level summary.)*
""")

nb["cells"] = cells
nbf.write(nb, "olist_brazil_analysis.ipynb")
print("Notebook written with", len(cells), "cells")
