import streamlit as st
import pandas as pd
from function.dashboard import latest_value, get_fred, get_yahoo

st.set_page_config(page_title="Trading Desk Simulator", page_icon="💼")

st.title("Welcome to my financial laboratory.")
st.markdown("""
Use the tabs on the left to navigate :
- **Pricing** : to price vanilla and exotic options
- **Commodities** : to see my trading signal
""")

fred_series = {
    "US CPI": "CPIAUCSL",
    "US UNEMPLOYEMENT": "UNRATE",
    "US GDP": "GDP",
    "FED RATE": "DFEDTARU",
    "US 10Y": "DGS10",
    "France Inflation": "CPALTT01FRM657N",
    "France Unemployment": "LRHUTTTTFRM156S",
    "ECB RATE": "ECBDFR"
}

market_series = {
    "GOLD": "GC=F",
    "OIL": "CL=F",
    "SP500": "^GSPC",
    "VIX": "^VIX"
}

macro_data = {}

for name, code in fred_series.items():

    df = get_fred(code)
    macro_data[name] = latest_value(df)

for name, ticker in market_series.items():

    df = get_yahoo(ticker)
    macro_data[name] = latest_value(df)

st.title("Key indicators of the day ")

col1, col2, col3, col4 = st.columns(4)

metrics = list(macro_data.items())

for i, (name, value) in enumerate(metrics):

    if i % 4 == 0:
        col1.metric(name, round(value,2))
    elif i % 4 == 1:
        col2.metric(name, round(value,2))
    elif i % 4 == 2:
        col3.metric(name, round(value,2))
    else:
        col4.metric(name, round(value,2))