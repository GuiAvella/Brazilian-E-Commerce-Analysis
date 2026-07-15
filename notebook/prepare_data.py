"""
Data preparation for the Olist Brazilian E-Commerce analysis.
Merges the 9 raw Olist tables into one analysis-ready, order-item-level
master dataframe, plus a few supporting aggregate tables used by the
notebook and the Streamlit dashboard.
"""
import os
import urllib.request
import pandas as pd
import numpy as np

RAW = "raw_data/"
OUT = "../data/"

GITHUB_BASE = "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/"
FILES = [
    "olist_customers_dataset.csv", "olist_geolocation_dataset.csv", "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv", "olist_order_reviews_dataset.csv", "olist_orders_dataset.csv",
    "olist_products_dataset.csv", "olist_sellers_dataset.csv", "product_category_name_translation.csv",
]

os.makedirs(RAW, exist_ok=True)
for fname in FILES:
    fpath = RAW + fname
    if not os.path.exists(fpath):
        print(f"Downloading {fname} ...")
        urllib.request.urlretrieve(GITHUB_BASE + fname, fpath)
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- load ----
orders     = pd.read_csv(RAW + "olist_orders_dataset.csv",
                          parse_dates=["order_purchase_timestamp", "order_approved_at",
                                       "order_delivered_carrier_date", "order_delivered_customer_date",
                                       "order_estimated_delivery_date"])
customers  = pd.read_csv(RAW + "olist_customers_dataset.csv")
items      = pd.read_csv(RAW + "olist_order_items_dataset.csv", parse_dates=["shipping_limit_date"])
payments   = pd.read_csv(RAW + "olist_order_payments_dataset.csv")
reviews    = pd.read_csv(RAW + "olist_order_reviews_dataset.csv",
                          parse_dates=["review_creation_date", "review_answer_timestamp"])
products   = pd.read_csv(RAW + "olist_products_dataset.csv")
sellers    = pd.read_csv(RAW + "olist_sellers_dataset.csv")
cat_trans  = pd.read_csv(RAW + "product_category_name_translation.csv")
geo        = pd.read_csv(RAW + "olist_geolocation_dataset.csv")

# Brazilian state name lookup (for readable labels on maps/charts)
STATE_NAMES = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul",
    "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins",
}

# ---------------------------------------------------------- clean/dedupe --
# Reviews: keep the latest review per order (a few orders have >1)
reviews = reviews.sort_values("review_answer_timestamp").drop_duplicates("order_id", keep="last")

# Payments: collapse multiple installments/rows per order into order-level totals
pay_agg = payments.groupby("order_id").agg(
    total_payment_value=("payment_value", "sum"),
    n_payment_types=("payment_type", "nunique"),
    max_installments=("payment_installments", "max"),
).reset_index()
pay_main = (payments.sort_values("payment_value", ascending=False)
            .drop_duplicates("order_id", keep="first")[["order_id", "payment_type"]]
            .rename(columns={"payment_type": "main_payment_type"}))
payments_o = pay_agg.merge(pay_main, on="order_id", how="left")

# Products: bring in English category names + fill missing category
products = products.merge(cat_trans, on="product_category_name", how="left")
products["product_category_name_english"] = products["product_category_name_english"].fillna("unknown")

# ------------------------------------------------------- item-level base --
df = (items
      .merge(orders, on="order_id", how="left")
      .merge(customers, on="customer_id", how="left")
      .merge(products[["product_id", "product_category_name_english", "product_weight_g",
                        "product_length_cm", "product_height_cm", "product_width_cm"]],
             on="product_id", how="left")
      .merge(sellers, on="seller_id", how="left")
      .merge(payments_o, on="order_id", how="left")
      .merge(reviews[["order_id", "review_score", "review_creation_date"]], on="order_id", how="left"))

df["customer_state_name"] = df["customer_state"].map(STATE_NAMES)
df["seller_state_name"] = df["seller_state"].map(STATE_NAMES)

# Derived fields
df["item_total"] = df["price"] + df["freight_value"]
df["freight_ratio"] = df["freight_value"] / df["price"].replace(0, np.nan)
df["purchase_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
df["purchase_year"] = df["order_purchase_timestamp"].dt.year
df["purchase_dow"] = df["order_purchase_timestamp"].dt.day_name()
df["purchase_hour"] = df["order_purchase_timestamp"].dt.hour
df["delivery_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
df["delivery_delay_days"] = (df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]).dt.days
df["is_late"] = df["delivery_delay_days"] > 0
df["cross_state_shipment"] = df["customer_state"] != df["seller_state"]
df["product_volume_cm3"] = df["product_length_cm"] * df["product_height_cm"] * df["product_width_cm"]

# Restrict to delivered orders for delivery/review-time-based analysis (keep a flag, don't drop from df)
delivered = df[df["order_status"] == "delivered"].copy()

# --------------------------------------------------- customer-level table -
cust_orders = (df.groupby("customer_unique_id")
               .agg(n_orders=("order_id", "nunique"),
                    total_spent=("item_total", "sum"),
                    avg_review=("review_score", "mean"),
                    state=("customer_state", "first"))
               .reset_index())
cust_orders["is_repeat"] = cust_orders["n_orders"] > 1

# ---------------------------------------------------------------- save ----
df.to_parquet(OUT + "master_items.parquet", index=False)
delivered.to_parquet(OUT + "delivered_items.parquet", index=False)
cust_orders.to_parquet(OUT + "customers_summary.parquet", index=False)

print("master_items:", df.shape)
print("delivered_items:", delivered.shape)
print("customers_summary:", cust_orders.shape)
print("date range:", df["order_purchase_timestamp"].min(), "->", df["order_purchase_timestamp"].max())
print("saved to", OUT)
