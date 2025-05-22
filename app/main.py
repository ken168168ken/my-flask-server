# 主程式 main.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

# 預設技術指標顯示顏色與圖例標籤
eng_map = {
    "SMA": "SMA",
    "MACD": "MACD",
    "KDJ": "KDJ",
    "M頭": "M-Head",
    "W底": "W-Bottom",
    "布林通道": "Bollinger Bands",
    "Combined": "Combined"
}
markers = {
    "SMA": ("o", "red"),
    "MACD": ("v", "purple"),
    "KDJ": ("^", "green"),
    "M頭": ("X", "orange"),
    "W底": ("*", "blue"),
    "布林通道": ("s", "magenta"),
    "Combined": ("D", "black")
}

# 初始化登入狀態
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 登入頁
if not st.session_state.logged_in:
    st.image("https://raw.githubusercontent.com/ken168168ken/k-platform/main/static/k_logo.png", width=80)
    st.title("🔐 K 技術分析平台 登入")
    username = st.text_input("帳號")
    password = st.text_input("密碼（任意填）", type="password")
    if st.button("登入"):
        if username:
            st.session_state.logged_in = True
            st.session_state.GITHUB_USER = username
            st.experimental_rerun()
        else:
            st.error("請輸入帳號。")
    st.stop()

# 主頁開始
st.image("https://raw.githubusercontent.com/ken168168ken/k-platform/main/static/k_logo.png", width=40)
st.markdown(f"已登入：`{st.session_state.GITHUB_USER}`")
st.title("📈 K 技術分析平台")
st.caption("這是一個整合技術指標、回測模組、股票數據分析的平台。")

symbol = st.text_input("📊 股票代碼 (例如：2330.TW 或 AAPL)", "TSLA")
years = st.slider("⏳ 回測年限 (年)", 1, 3, 1)
options = st.multiselect("📉 選擇技術指標", ["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"], default=["均線"])

signals = {}

# 技術指標參數欄位
if "均線" in options:
    st.subheader("均線 SMA")
    sma_short = st.number_input("SMA 短期 window", 1, 120, 10)
    sma_long = st.number_input("SMA 長期 window", 1, 300, 50)
    show_sma_cross = st.checkbox("顯示 SMA 金叉死叉點")

if "MACD" in options:
    st.subheader("MACD")
    macd_fast = st.number_input("MACD 快線 span", 1, 50, 12)
    macd_slow = st.number_input("MACD 慢線 span", 1, 50, 26)
    macd_signal = st.number_input("MACD 信號線 span", 1, 30, 9)
    show_macd_cross = st.checkbox("顯示 MACD 金叉死叉點")

if "KDJ" in options:
    st.subheader("KDJ")
    kdj_n = st.number_input("KDJ 計算期間", 1, 30, 14)
    kdj_k = st.number_input("K 平滑期數", 1, 30, 3)
    kdj_d = st.number_input("D 平滑期數", 1, 30, 3)

if "布林通道" in options:
    st.subheader("布林通道")
    bb_period = st.number_input("布林通道期間 (Period)", 1, 100, 20)
    bb_width = st.number_input("布林通道寬度 k (倍數)", 0.1, 5.0, 2.0, step=0.1)

if st.button("▶️ 執行分析"):
    df = yf.download(symbol, period=f"{years}y")
    df.dropna(inplace=True)
    fig, ax = plt.subplots()
    ax.plot(df.index, df["Close"], label="Close Price")

    # 技術指標模擬訊號（以下僅為示意）
    if "均線" in options:
        signal = df["Close"].rolling(sma_short).mean() > df["Close"].rolling(sma_long).mean()
        signals["SMA"] = signal.astype(int)

    if "MACD" in options:
        ema_fast = df["Close"].ewm(span=macd_fast).mean()
        ema_slow = df["Close"].ewm(span=macd_slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=macd_signal).mean()
        signal = (macd > signal_line)
        signals["MACD"] = signal.astype(int)

    if "KDJ" in options:
        low_min = df["Low"].rolling(kdj_n).min()
        high_max = df["High"].rolling(kdj_n).max()
        rsv = (df["Close"] - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(com=kdj_k).mean()
        d = k.ewm(com=kdj_d).mean()
        signal = (k > d)
        signals["KDJ"] = signal.astype(int)

    if "布林通道" in options:
        ma = df["Close"].rolling(bb_period).mean()
        std = df["Close"].rolling(bb_period).std()
        upper = ma + bb_width * std
        lower = ma - bb_width * std
        signal = (df["Close"] < lower) | (df["Close"] > upper)
        signals["布林通道"] = signal.astype(int)

    st.subheader("📊 各指標勝率")
    for ind, ser in signals.items():
        rate = int(float(ser.mean()) * 100)
        st.write(f"• {eng_map[ind]} 勝率：{rate}%")

    st.subheader("📈 價格與進出場點圖")
    for ind, ser in signals.items():
        if ser.sum().item() == 0:
            continue
        pts = ser[ser == 1].index
        m, c = markers[ind]
        ax.scatter(pts, df.loc[pts, "Close"], marker=m, color=c, s=80, label=eng_map[ind])

    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    st.pyplot(fig, use_container_width=True)
