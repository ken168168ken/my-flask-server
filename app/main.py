import os
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf  # 或者你拿数据的方式

# --- Page config: 一定要最前面 ---
st.set_page_config(page_title="K Technical Analysis", page_icon="logo.png")

# --- Login page ---
if 'GITHUB_USER' not in st.session_state:
    st.title("🔐 K 技術分析平台 登入")
    user = st.text_input("帳號", value=os.getenv("GITHUB_USER", ""), key="login_user")
    pwd  = st.text_input("密碼 (任意填)", type="password", key="login_pwd")
    if st.button("登入"):
        st.session_state.GITHUB_USER = user
        st.experimental_rerun()
    st.stop()

# --- Main UI ---
# 顶部 Logo 圆形
col1, col2 = st.columns([1, 9])
with col1:
    img = Image.open("logo.png").convert("RGBA")
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    mask_draw = Image.new("L", (w, h), 0)
    mask_draw = Image.new("L", (w, h), 0)
    draw = Image.new("L", (w, h), 0)
    # 生成圆形 Mask
    circle = Image.new("L", (w, h), 0)
    import PIL.ImageDraw as D
    d = D.Draw(circle)
    d.ellipse((0, 0, w, h), fill=255)
    img.putalpha(circle)
    st.image(img, width=80)
with col2:
    st.markdown(f"<div style='text-align:right; font-size:14px;'>🔒 已登入帳號：`{st.session_state.GITHUB_USER}`</div>", unsafe_allow_html=True)

st.header("K 技術分析平台")
st.write("這是一個整合技術指標、回測模組、股票數據分析的平台。")


# --- Query inputs ---
st.subheader("✅ 查詢條件")
symbol = st.text_input("股票代碼 (例：2330.TW 或 AAPL)", "")
indicators = st.multiselect(
    "選擇技術指標",
    options=["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"],
)
years = st.slider("回測年限 (年)", 1, 3, 3)

if not symbol or not indicators:
    st.info("請輸入股票代碼並至少選一個技術指標。")
    st.stop()

if st.button("執行分析"):
    # --- 1. 下載數據 ---
    end = pd.Timestamp.today()
    start = end - pd.DateOffset(years=years)
    df = yf.download(symbol, start=start, end=end)
    df.dropna(inplace=True)

    # --- 2. 計算 signals dict ---
    signals = {}
    # 均線
    if "均線" in indicators:
        sma = df["Close"].rolling(20).mean()
        signals["均線"] = df["Close"] > sma
    # MACD
    if "MACD" in indicators:
        exp1 = df["Close"].ewm(span=12).mean()
        exp2 = df["Close"].ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        signals["MACD"] = macd > signal
    # KDJ
    if "KDJ" in indicators:
        low_k = df["Low"].rolling(9).min()
        high_k = df["High"].rolling(9).max()
        rsv = 100 * (df["Close"] - low_k) / (high_k - low_k)
        k = rsv.ewm(com=2).mean()
        d = k.ewm(com=2).mean()
        j = 3 * k - 2 * d
        signals["KDJ"] = (j > k) & (k > d)
    # M頭 & W底
    if "M頭" in indicators:
        signals["M頭"] = df["Close"] < df["Close"].shift(1)
    if "W底" in indicators:
        signals["W底"] = df["Close"] > df["Close"].shift(1)
    # Bollinger Bands
    if "布林通道" in indicators:
        mb = df["Close"].rolling(20).mean()
        ub = mb + 2 * df["Close"].rolling(20).std()
        lb = mb - 2 * df["Close"].rolling(20).std()
        signals["布林通道"] = (df["Close"] < lb) | (df["Close"] > ub)
    # Combined
    if len(indicators) > 1:
        comb = pd.Series(True, index=df.index)
        for ind in indicators:
            comb &= signals[ind]
        signals["合成"] = comb

    # --- 3. 各指標勝率 (示意) ---
    st.subheader("📊 查詢結果圖表")
    for ind, ser in signals.items():
        win_rate = int(ser.mean() * 100)
        label = {
            "均線": "SMA",
            "MACD": "MACD",
            "KDJ": "KDJ",
            "M頭": "M-Head",
            "W底": "W-Bottom",
            "布林通道": "Bollinger Bands",
            "合成": "Combined"
        }[ind]
        st.markdown(f"- {label} 勝率：{win_rate}%")

    # --- 4. Price & Entry Signals (英文标签) ---
    eng_map = {
        "均線": "SMA",
        "MACD": "MACD",
        "KDJ": "KDJ",
        "M頭": "M-Head",
        "W底": "W-Bottom",
        "布林通道": "Bollinger Bands",
        "合成": "Combined"
    }
    markers = {
        "均線":        ("o", "orange"),
        "MACD":       ("^", "green"),
        "KDJ":        ("s", "red"),
        "M頭":        ("v", "purple"),
        "W底":        ("P", "brown"),
        "布林通道":    ("*", "pink"),
        "合成":        ("X", "black"),
    }
    st.subheader("📈 Price & Entry Signals")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df.index, df["Close"], label="Close Price", color="blue")
    # 预先画空 scatter 以便 legend
    for ind in signals:
        mk, col = markers[ind]
        ax.scatter([], [], marker=mk, color=col, label=eng_map[ind])
    # 真正画进出点
    for ind, ser in signals.items():
        pts = ser[ser].index
        mk, col = markers[ind]
        ax.scatter(pts, df.loc[pts, "Close"], marker=mk, color=col, s=80)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    st.pyplot(fig, use_container_width=True)
