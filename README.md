# Brazil's Marketplace in Motion 🇧🇷
### Final Individual Project — Data Visualization, Summer 2026

An end-to-end analysis of the **Brazilian E-Commerce Public Dataset by Olist** — 100k+ real orders placed on Olist's multi-seller marketplace between 2016 and 2018.

## Project structure

```
.
├── app.py                          # entry point — page config + st.navigation (12 pages)
├── utils.py                        # shared cached loader + persisted sidebar filters + chart style
├── requirements.txt
├── pages/                          # one page per analytical question
│   ├── 01_delivery_time_by_state.py       Q1  · slower delivery ↔ lower review scores?
│   ├── 02_revenue_by_category.py          Q2  · which categories drive revenue?
│   ├── 03_freight_ratio_by_category.py    Q3  · costliest categories to ship?
│   ├── 04_delivery_delay_vs_review.py     Q4  · does a late delivery cost stars?
│   ├── 05_state_value_installments.py     Q5  · who spends most, and how do they pay?
│   ├── 06_price_tier_vs_review.py         Q6  · does price buy satisfaction?
│   ├── 07_weekly_order_rhythm.py          Q7  · weekly shopping rhythm over time?
│   ├── 08_installments_vs_order_value.py  Q8  · installments vs. basket size?
│   ├── 09_seller_revenue_concentration.py Q9  · how concentrated is seller revenue?
│   ├── 10_cross_state_shipping.py         Q10 · how often does shipping cross state lines?
│   ├── 11_product_volume_vs_freight.py    Q11 · product size vs. freight cost?
│   └── 12_repeat_customers.py             Q12 · are repeat customers worth more?
├── data/                            # pre-merged Parquet files (shared by notebook + dashboard)
│   ├── master_items.parquet
│   ├── delivered_items.parquet
│   └── customers_summary.parquet
├── notebook/
│   ├── olist_brazil_analysis.ipynb  # same 12 questions, EDA, narrative — the source of truth
│   ├── olist_brazil_analysis.html
│   ├── olist_brazil_analysis.pdf
│   ├── build_notebook.py
│   └── prepare_data.py              # downloads + merges the 9 raw Olist CSVs into data/
├── presentation/
│   ├── Brazil_Marketplace_in_Motion.pdf
│   └── Brazil_Marketplace_in_Motion.pptx
└── README.md
```

**Dashboard files live at the project root** (`app.py`, `utils.py`, `requirements.txt`, `pages/`) — this is what Streamlit Community Cloud expects when you point it at `app.py` directly. `data/` sits alongside them, and `notebook/` / `presentation/` hold the other two deliverables.

## How the dashboard is wired together

- **`utils.py`**
  - `load_data()` — `@st.cache_data`-cached read of the three Parquet files in `data/`, shared by every page.
  - `sidebar_filters()` — the sidebar (year / state / category) renders identically on all 12 pages and keeps its selections alive across page switches via the `st.session_state[key] = st.session_state[key]` keep-alive pattern.
  - `style()` / `page_header()` — one shared chart theme and page-title helper so every page looks and reads the same way.
- **`app.py`** sets page config + light CSS once, then registers all 12 pages via `st.navigation([...])`, each labelled with its question.
- **Every page** follows the same skeleton:
  ```python
  items, delivered, customers = load_data()
  f_items, f_delivered, f_customers = sidebar_filters(items, delivered, customers)
  page_header("The question, as a sentence")
  # 2-3 KPIs → one chart that answers the question → an expander with the raw numbers
  ```
- **Design rules applied throughout:** no pie charts (Q12's "one-time vs. repeat" comparison is a bar chart, not a donut), no red/green pairing (blue `#2E75B6` / orange `#E07B39` / grey `#AAAAAA` / green `#3F9C6B` used deliberately, never red-vs-green together), one insight-stating chart title per page, KPI cards up top for the 5-second test, and a progressive-disclosure expander for the underlying data table.

## Dataset

**Source:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle), mirrored officially by Olist at [`olist/work-at-olist-data`](https://github.com/olist/work-at-olist-data). Real, anonymised commercial data — 9 relational CSV files covering orders, customers, products, sellers, payments, reviews, and geolocation.

The raw CSVs are **not** committed to this repo; `notebook/prepare_data.py` downloads them automatically from the GitHub mirror and builds the merged Parquet files in `data/`.

- **Numerical:** price, freight, product weight/dimensions, review score
- **Categorical:** 72 product categories, payment type, order status
- **Spatial:** customer & seller state/city/zip + lat-lon geolocation
- **Temporal:** order purchase/approval/delivery timestamps, 2016–2018

## Running locally

```bash
# 1. Rebuild the merged dataset (downloads raw CSVs on first run, writes to data/)
cd notebook
pip install pandas numpy pyarrow
python prepare_data.py
cd ..

# 2. Notebook (optional — the exports are already included)
pip install jupyter plotly kaleido statsmodels
jupyter notebook notebook/olist_brazil_analysis.ipynb

# 3. Dashboard — run FROM THE PROJECT ROOT (utils.py reads "data/...")
pip install -r requirements.txt
streamlit run app.py
```

## Deploying the dashboard live

1. Push this repo to a **public** GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/), sign in with GitHub, and click **New app**.
3. Point it at this repo, branch `main`, main file path `app.py` (no subfolder).
4. Deploy — Streamlit Community Cloud installs `requirements.txt` automatically.
5. Add the resulting live URL to this README and to the presentation.

## Key takeaways

1. **Delivery speed drives satisfaction more than anything else** — late orders lose almost a full star, and slow-delivery states rate consistently lower (Q1, Q4).
2. **Revenue is geographically and structurally concentrated** — São Paulo dominates as commercial hub, and the top ~20% of sellers generate ~82% of revenue (Q9, Q10).
3. **Price doesn't buy satisfaction** — review scores are flat across price tiers within every top category (Q6); the satisfaction problem is operational, not pricing.
4. **Freight cost is a size/weight game** — bulky, low-value categories (furniture, construction) carry the worst freight-to-price ratio and the steepest volume-to-cost slope (Q3, Q11).
5. **2018 growth was healthy and increasingly weekday-driven**, led by health & beauty and watches/gifts (Q2, Q7).
6. **Repeat purchase is rare (~3%) but valuable** — repeat customers spend ~2x more per head (Q12), making retention a clear growth lever.
