# utils.py — shared by every page
import pandas as pd
import streamlit as st

STATE_NAMES = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul",
    "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins",
}

# CVD-safe palette — reused by every page (blue/orange/grey, never red-green)
BLUE, ORANGE, GREY, GREEN, BLACK, WHITE = "#2E75B6", "#E07B39", "#AAAAAA", "#3F9C6B", "#000000", "#FFFFFF"
DARKRED = "#8B0000"
CVD_SEQ = ["#2E75B6", "#56B4E9", "#3F9C6B", "#E69F00", "#E07B39", "#CC79A7"]


# ─────────────────────────────────────────────────────────────────────────────
# cached loader — the expensive merge already happened in notebook/prepare_data.py;
# here we just read the pre-merged Parquet files once and share them across
# every page (same function = same cache entry everywhere)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    items = pd.read_parquet('data/master_items.parquet')
    delivered = pd.read_parquet('data/delivered_items.parquet')
    customers = pd.read_parquet('data/customers_summary.parquet')
    return items, delivered, customers


# ─────────────────────────────────────────────────────────────────────────────
# initialise filter keys once + keep them alive on every run.
# Streamlit deletes widget keys not rendered in the current run — without the
# re-assignment, filters would reset on every page switch.
# ─────────────────────────────────────────────────────────────────────────────
def init_filters(items):
    defaults = {
        'flt_years': sorted(items['purchase_year'].dropna().unique().tolist()),
        'flt_states': [],
        'flt_cats': [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value                   # initialise once
        else:
            st.session_state[key] = st.session_state[key]   # keep alive across pages


# ─────────────────────────────────────────────────────────────────────────────
# shared sidebar — called at the top of every page.
# Widgets use key= ONLY (no default=/value=): values come from session_state,
# passing both would trigger Streamlit's double-set warning.
# ─────────────────────────────────────────────────────────────────────────────
def sidebar_filters(items, delivered, customers):
    init_filters(items)
    years = sorted(items['purchase_year'].dropna().unique().tolist())
    states = sorted(items['customer_state'].dropna().unique().tolist())
    cats = sorted(items['product_category_name_english'].dropna().unique().tolist())

    with st.sidebar:
        st.header('🔎 Filters')
        st.multiselect('Purchase year', years, key='flt_years')
        st.multiselect('Customer state', states, key='flt_states')
        st.multiselect('Product category', cats, key='flt_cats')
        st.divider()
        # BBD: tell users about data decisions made on their behalf
        st.caption('Leave a filter empty to include every value for that field.')
        st.caption(
            'Data: Olist Brazilian E-Commerce (2016–2018) · '
            '[GitHub mirror](https://github.com/olist/work-at-olist-data)'
        )

    f_items, f_delivered = items, delivered
    if st.session_state.flt_years:
        f_items = f_items[f_items['purchase_year'].isin(st.session_state.flt_years)]
        f_delivered = f_delivered[f_delivered['purchase_year'].isin(st.session_state.flt_years)]
    if st.session_state.flt_states:
        f_items = f_items[f_items['customer_state'].isin(st.session_state.flt_states)]
        f_delivered = f_delivered[f_delivered['customer_state'].isin(st.session_state.flt_states)]
    if st.session_state.flt_cats:
        f_items = f_items[f_items['product_category_name_english'].isin(st.session_state.flt_cats)]
        f_delivered = f_delivered[f_delivered['product_category_name_english'].isin(st.session_state.flt_cats)]

    if f_items.empty:
        st.warning('No orders match the current filters.')
        st.stop()

    f_customers = customers
    if st.session_state.flt_states:
        f_customers = f_customers[f_customers['state'].isin(st.session_state.flt_states)]

    return f_items, f_delivered, f_customers


def style(fig, title, height=440):
    """Shared chart styling: white background, Arial, decluttered grid."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, family='Arial', color=BLACK), x=0.01),
        plot_bgcolor='white', paper_bgcolor='white',
        font=dict(family='Arial', size=12, color=BLACK), 
        height=height,
        margin=dict(l=10, r=10, t=55, b=10),
        legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(color="#000000"))
    )
    fig.update_xaxes(
        showgrid=False, 
        zeroline=False,
        title_font=dict(color=BLACK),   # axis title color
        tickfont=dict(color=BLACK),     # tick label color (4.2, 4.1, etc.)
    )
    fig.update_yaxes(
        showgrid=True, 
        gridcolor="#000000", 
        zeroline=False,
        title_font=dict(color=BLACK),   # axis title color
        tickfont=dict(color=BLACK),     # tick label color (4.2, 4.1, etc.)
    )
    return fig


def page_header(question, caption=None):
    """Every page opens the same way: the analytical question as the title."""
    st.title(question)
    if caption:
        st.caption(caption)
