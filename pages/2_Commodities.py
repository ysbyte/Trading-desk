import streamlit as st
import matplotlib.pyplot as plt
from function.commodities import*

st.set_page_config(layout="wide")

st.title("Commodities Module")
st.title("Market Overview : WTI & Brent")

df = get_oil_data()

st.subheader("Oil Prices")

last_wti = df["WTI"].iloc[-1]
last_brent = df["Brent"].iloc[-1]

col1, col2 = st.columns(2)
col1.metric("Last WTI price", f"{last_wti:.2f} $")
col2.metric("Last Brent price", f"{last_brent:.2f} $")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df.index, df["WTI"], label="WTI")
ax.plot(df.index, df["Brent"], label="Brent")
ax.set_title("WTI vs Brent Prices")
ax.legend()
ax.grid()
st.pyplot(fig)

st.subheader("Key Metrics")

returns = compute_returns(df)
vol_wti = annual_vol(returns["WTI"]) * 100
vol_brent = annual_vol(returns["Brent"]) * 100

col1, col2, col3 = st.columns(3)

col1.metric("WTI Sharpe", round(sharpe(returns["WTI"]), 2))
col2.metric("Brent Sharpe", round(sharpe(returns["Brent"]), 2))
col3.metric("Correlation", round(returns.corr().iloc[0,1], 2))

col4, col5, col6 = st.columns(3)
col4.metric("WTI Volatility", f"{vol_wti:.1f}%")
col5.metric("Brent Volatility", f"{vol_brent:.1f}%")
col6.metric("Max Drawdown (WTI)", f"{max_drawdown(df['WTI']):.1f}%")

col7, col8, col9 = st.columns(3)
col7.metric("Momentum (20d) WTI", f"{compute_momentum(df["WTI"]):.2f}%")
col8.metric("Momentum (20d) Brent", f"{compute_momentum(df["Brent"]):.1f}%")
col9.metric("Max Drawdown (Brent)", f"{max_drawdown(df['Brent']):.1f}%")

st.subheader("US Crude Oil Inventories")

api_key="YpBLdEK8anEKhCEcQbqypYbaMiBU1d6JWJUvtLs4"
df_eia=get_eia_inventory(api_key)
last_total = df_eia["inventory"].iloc[-1]
last_var = df_eia["variation"].iloc[-1]
avg_4w_var = df_eia["variation"].tail(4).mean()

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("US Total Inventories", f"{last_total:.1f} M bbl")
col_m2.metric("Weekly Change (Current)", f"{last_var:.2f} M", delta_color="inverse")
col_m3.metric("4W Average Change", f"{avg_4w_var:.2f} M", delta_color="inverse")

df_plot = df_eia.tail(52)
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.subheader("Stock Levels")
    fig1, ax1 = plt.subplots()
    ax1.plot(df_plot.index, df_plot["inventory"]) 
    ax1.grid(True) 
    st.pyplot(fig1)

with col_g2:
    st.subheader("Weekly Inventory Change")
    fig2, ax2 = plt.subplots()
    ax2.bar(df_plot.index, df_plot["variation"],width=5)
    ax2.axhline(0, color='black', linewidth=1)
    ax2.grid(True)
    st.pyplot(fig2)

st.subheader("Futures Forward Curve")

col10 , col11= st.columns(2)
with col10:
    oil_type=st.selectbox("Choose Oil Reference", ["Brent","WTI"])
with col11:
    month=st.selectbox("Choose Futures Month", [i for i in range(1,13)])

fig_to_show = futures_curve(symbol=oil_type, months=month)
if fig_to_show:
    st.pyplot(fig_to_show)
else:
    st.warning(f"Data for {oil_type} futures is currently unavailable on Yahoo Finance.")

st.title("Trading Strategy : Brent-Oil spread")

spread = compute_spread(df)
z = zscore(spread)

st.subheader("Spread (Brent-WTI)")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(spread.index, spread, label="Spread", color="black")
last_date = spread.index[-1]
last_val = spread.iloc[-1]
ax.plot(last_date, last_val, 'ro', markersize=5)
ax.annotate(
    f"{last_val:.2f} $", 
    xy=(last_date, last_val),       # Le point à pointer (le dernier prix)
    xytext=(8, 0),                  # On décale le texte de 8 pixels à droite
    textcoords="offset points",     # On dit à Python que 8 c'est des pixels, pas des dates
    va="center",                    # Centré verticalement sur le point
    color="red",
    fontweight="bold",
    bbox=dict(facecolor='white', alpha=0.8, edgecolor='red', boxstyle='round,pad=0.2')
)
ax.set_title("WTI - Brent Spread")
ax.axhline(spread.mean(), linestyle="--", label="Mean")
ax.legend()
ax.grid()
st.pyplot(fig)

st.subheader("Z-Score")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(z.index, z, label="Z-score", color="purple")
ax.axhline(1, linestyle="--", color="red")
ax.axhline(-1, linestyle="--", color="green")
ax.set_title("Z-score (Mean Reversion Signal)")
ax.legend()
ax.grid()

st.pyplot(fig)

s = signal(z)

pnl, strat_r, sharpe_val, max_dd = backtest(df, s)

st.subheader("Strategy Performance")

col1, col2 = st.columns(2)
col1.metric("Sharpe", round(sharpe_val, 2))
col2.metric("Max Drawdown", round(max_dd, 2))

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(pnl.index, pnl, label="PnL", color="blue")
ax.set_title("Cumulative PnL")
ax.legend()
ax.grid()

st.pyplot(fig)

