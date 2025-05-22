# 主程式 main.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# 初始化頁面
st.set_page_config(page_title="K 技術分析平台", layout="wide")
st.title("📈 K 技術分析平台")

# 登入（簡化版）
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    username = st.text_input("帳號", value="")
    password = st.text_input("密碼（任意填）", type="password")
    if st.button("登入"):
        if username:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
    st.stop()

# 主介面
st.markdown(f"已登入：`{st.session_state.username}`")
st.markdown("這是一個整合技術指標、回測模組、股票數據分析的平台。")

symbol = st.text_input("📊 股票代碼 (例如：2330.TW 或 AAPL)", "TSLA")
years = st.slider("⏳ 回測年限 (年)", 1, 3, 1)

options = st.multiselect(
    "📈 選擇技術指標",
    ["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"],
    default=["均線"]
)

# 技術指標參數區塊
params = {}
if "均線" in options:
    st.markdown("### 均線 SMA")
    sma_short = st.number_input("SMA 短期 window", 5, 50, 10)
    sma_long = st.number_input("SMA 長期 window", 10, 200, 50)
    show_cross = st.checkbox("顯示 SMA 金叉死叉點", value=True)
    params["SMA"] = (sma_short, sma_long, show_cross)

if "MACD" in options:
    st.markdown("### MACD")
    macd_fast = st.number_input("MACD 快線 span", 5, 50, 12)
    macd_slow = st.number_input("MACD 慢線 span", 10, 100, 26)
    macd_signal = st.number_input("MACD 訊號線 span", 5, 50, 9)
    params["MACD"] = (macd_fast, macd_slow, macd_signal)

if "KDJ" in options:
    st.markdown("### KDJ")
    kdj_period = st.number_input("KDJ 計算期間", 5, 50, 14)
    params["KDJ"] = kdj_period

if "布林通道" in options:
    st.markdown("### 布林通道")
    bb_period = st.number_input("布林通道期間 (Period)", 10, 60, 20)
    bb_width = st.number_input("布林通道寬度 k (倍數)", 1.0, 5.0, 2.0)
    params["Bollinger"] = (bb_period, bb_width)

# 執行分析按鈕
if st.button("▶️ 執行分析"):
    df = yf.download(symbol, period=f"{years}y")
    if df.empty:
        st.warning("查無資料，請確認股票代碼是否正確。")
        st.stop()

    # 計算收盤價
    close = df["Close"]
    signals = {}
    markers = {}

    if "SMA" in params:
        short, long, show_cross = params["SMA"]
        sma_short = close.rolling(window=short).mean()
        sma_long = close.rolling(window=long).mean()
        golden = (sma_short > sma_long) & (sma_short.shift() <= sma_long.shift())
        death = (sma_short < sma_long) & (sma_short.shift() >= sma_long.shift())
        signal = golden | death
        signals["SMA"] = signal
        markers["SMA"] = ("o", "red")

    # 勝率區塊（示意）
    st.markdown("## 📊 各指標勝率")
    for name, ser in signals.items():
        rate = int((ser.mean() * 100) if not ser.empty else 0)
        st.markdown(f"- {name} 勝率：{rate}%")

    # 圖表區塊
    st.markdown("## 📈 價格與進出場點圖")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df.index, df["Close"], label="Close Price")

    for ind, ser in signals.items():
        if ser.sum() == 0:
            continue
        pts = ser[ser].index
        m, c = markers[ind]
        ax.scatter(pts, df.loc[pts, "Close"], marker=m, color=c, s=80, label=ind)

    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    st.pyplot(fig, use_container_width=True)

    # 回測表格（可加上買賣點範例）
    st.markdown("### 📋 回測範例與詳細數據（待擴充）")
