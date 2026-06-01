import requests
import pandas as pd
import streamlit as st
import time

FRED_KEY = "f19d3e41fcd9e8e36113d63a74232cbb"

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"

@st.cache_data(ttl=3600)
def get_fred(series):

    params = {
        "series_id": series,
        "api_key": FRED_KEY,
        "file_type": "json"
    }

    time.sleep(0.5)
    r = requests.get(FRED_URL, params=params)
    data = r.json()

    if "observations" not in data:
        return None

    df = pd.DataFrame(data["observations"])

    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def get_yahoo(ticker):

    params = {
        "interval": "1d",
        "range": "1y"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(YAHOO_URL + ticker, params=params, headers=headers)

    data = r.json()

    timestamps = data["chart"]["result"][0]["timestamp"]
    prices = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]

    df = pd.DataFrame({
        "date": pd.to_datetime(timestamps, unit="s"),
        "value": prices
    })
    return df

def latest_value(df):
    return df["value"].dropna().iloc[-1]


