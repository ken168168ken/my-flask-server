# 主程式 main.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# 圖示樣式定義
markers = {
    "SMA": ("o", "red"),
    "MACD": ("v", "blue"),
    "KDJ": ("s", "green"),
    "M-Head": ("^", "purple"),
    "W-Bottom": ("*", "orange"),
    "Bollinger Bands": ("X", "brown"),
    "Combined": ("+", "black"),
}

# 英文對照圖示名稱（圖例）
eng_map = {
    "均線": "SMA",
    "MACD": "MACD",
    "KDJ": "KDJ",
    "M頭": "M-Head",
    "W底": "W-Bottom",
    "布林通道": "Bollinger Bands",
    "合成": "Combined",
}

st.set_page_config(page_title="K 技術分析平台")
st.title("📈 K 技術分析平台")
st.caption("這是一個整合技術指標、回測模組、股票數據分析的平台。")

symbol = st.text_input("📉 股票代碼 (例如：2330.TW 或 AAPL)", value="TSLA")
year_range = st.slider("📆 回測年限 (年)", 1, 3, 1)
indicators = st.multiselect("📊 選擇技術指標", ["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"], default=["均線"])

# 參數區塊
if "均線" in indicators:
    sma_short = st.number_input("SMA 短期 window", 1, 100, 10)
    sma_long = st.number_input("SMA 長期 window", 1, 300, 50)
    show_cross = st.checkbox("顯示 SMA 金叉死叉點")

if "MACD" in indicators:
    macd_fast = st.number_input("MACD 快線 span", 1, 100, 12)
    macd_slow = st.number_input("MACD 慢線 span", 1, 100, 26)
    macd_signal = st.number_input("MACD 信號線 span", 1, 100, 9)

if "KDJ" in indicators:
    kdj_period = st.number_input("KDJ 計算期間", 1, 100, 14)

if "布林通道" in indicators:
    bb_period = st.number_input("布林通道期間 (Period)", 1, 100, 20)
    bb_width = st.number_input("布林通道寬度 (k 倍數)", 0.1, 5.0, 2.0)

if st.button("▶️ 執行分析"):
    df = yf.download(symbol, period=f"{year_range}y")
    df.dropna(inplace=True)

    signals = {}

    # 均線金叉死叉判斷
    if "均線" in indicators:
        df["sma_short"] = df["Close"].rolling(window=sma_short).mean()
        df["sma_long"] = df["Close"].rolling(window=sma_long).mean()
        cross = (df["sma_short"] > df["sma_long"]) & (df["sma_short"].shift() <= df["sma_long"].shift())
        signals["SMA"] = cross if show_cross else pd.Series([False] * len(df), index=df.index)

    # 其他指標範例（僅保留 SMA 測試）
    # 加入 MACD、KDJ、布林等邏輯可另補上

    # 合成信號
    if len(signals) >= 2:
        comb = pd.Series([True] * len(df), index=df.index)
        for ser in signals.values():
            comb &= ser
        signals["Combined"] = comb

    # 顯示勝率
    st.subheader("📊 各指標勝率")
    for ind, ser in signals.items():
        if ser.sum() > 0:
            rate = int(float(ser.mean()) * 100)
            st.markdown(f"- {eng_map.get(ind, ind)} 勝率：{rate}%")

    # 畫圖
    st.subheader("📈 價格與進出場點圖")
    fig, ax = plt.subplots()
    ax.plot(df.index, df["Close"], label="Close Price")
    for ind, ser in signals.items():
        if ser.sum() == 0:
            continue
        pts = ser[ser].index
        m, c = markers[ind]
        ax.scatter(pts, df.loc[pts, "Close"], marker=m, color=c, s=80, label=eng_map.get(ind, ind))
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    st.pyplot(fig, use_container_width=True)
