import streamlit as st
from function.black_scholes import bs_price, bs_greeks
from function.monte_carlo import monte_carlo_price
from function.monte_carlo import monte_carlo_price_asian
from function.monte_carlo import monte_carlo_price_lookback
from function.monte_carlo import monte_carlo_price_barrier
import numpy as np
import matplotlib.pyplot as plt

st.title("Pricing Module")
st.write("Feel free to adjust all the settings on the left")

st.sidebar.header("Pricing Settings")
S = st.sidebar.number_input("Spot (S)", value=100.0, step=0.1)
K = st.sidebar.number_input("Strike (K)", value=100.0, step=0.1)
T = st.sidebar.number_input("Maturity (en années, T)", value=1.0, step=0.1)
r = st.sidebar.number_input("Risk-free Rate (r)", value=0.05)
sigma = st.sidebar.number_input("Volatility (σ)", value=0.2)
option_type = st.sidebar.selectbox("Option Type", ["call", "put"])
st.sidebar.header("Settings for barrier options")
barrier_type=st.sidebar.selectbox("Type of barrier", ["knock-in", "knock-out"])
B=st.sidebar.number_input("Barrier", value=100.0, step=0.1)

bs = bs_price(S, K, T, r, sigma, option_type)
greeks = bs_greeks(S, K, T, r, sigma, option_type)
mc = monte_carlo_price(S, K, T, r, sigma, option_type, N=50000)

st.subheader("Results for the vanilla option")
col1, col2 = st.columns(2)
col1.metric("Black-Scholes Price", f"{bs:.4f}")
col2.metric("Monte Carlo Price", f"{mc:.4f}")

st.subheader("Greeks")
st.write(greeks)

spots = np.linspace(S*0.5, S*1.5, 50)
prices = [bs_price(s, K, T, r, sigma, option_type) for s in spots]

fig, ax = plt.subplots()
ax.plot(spots, prices, label="Black-Scholes Price")
ax.set_xlabel("Spot")
ax.set_ylabel("Option price")
ax.legend()
st.pyplot(fig)

o_asian=monte_carlo_price_asian(S,K,T,r,sigma,option_type,N=50000,M=100)
o_lookback=monte_carlo_price_lookback(S,K,T,r,sigma,option_type,N=50000,M=100)
o_barrier=monte_carlo_price_barrier(S,K,T,B,r,sigma,option_type,barrier_type,N=50000,M=100)

st.subheader("Results for some exotic options")

col3,col4,col5 = st.columns(3)
col3.metric("Asian option price", f"{o_asian:.4f}")
col4.metric("Lookback option price", f"{o_lookback:.4f}")
col5.metric("Barrier option price", f"{o_barrier:.4f}")