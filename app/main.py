import os
import streamlit as st
from PIL import Image, ImageDraw
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# —————— 登入流程 ——————
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    try:
        raw = Image.open("logo.png").convert("RGBA")
        w, h = raw.size
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).ellipse((0,0,w,h), fill=255)
        raw.putalpha(mask)
        st.image(raw, width=120)
    except:
        st.write("⚠️ Logo 載入失敗")
    st.title("🔐 K 技術分析平台 登入")
    user_in = st.text_input("帳號", "")
    pwd_in  = st.text_input("密碼 (任意填)", type="password")
    if st.button("登入"):
        if user_in and user_in == os.getenv("GITHUB_USER",""):
            st.session_state.logged_in = True
            st.session_state.user = user_in
            st.experimental_rerun()
        else:
            st.error("登入失敗，請檢查帳號")
    st.stop()

# —————— 主頁 Config ——————
st.set_page_config(page_title="K 技術分析平台", page_icon="logo.png", layout="wide")
col1, col2 = st.columns([1,9])
with col1:
    try:
        st.image(raw, width=80)
    except:
        pass
with col2:
    st.markdown(f"<div style='text-align:right'>🔐 已登入：`{st.session_state.user}`</div>",
                unsafe_allow_html=True)

st.title("K 技術分析平台")
st.write("這是一個整合技術指標、回測模組、自選股管理的分析平台。")
st.write("---")

# —————— 查詢條件 ——————
st.subheader("✅ 查詢條件")
ticker = st.text_input("🔍 股票代碼 (例：2330.TW 或 AAPL)", "").upper().strip()
indicators = st.multiselect(
    "📊 選擇技術指標",
    ["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"]
)
years = st.slider("⏳ 回測年限", 1, 5, 1)

# 動態參數
params = {}
if "均線" in indicators:
    st.subheader("— 均線 參數")
    params["ma_s"] = st.number_input("短期 MA", 2, 200, 5)
    params["ma_l"] = st.number_input("長期 MA", 5, 300, 20)
if "MACD" in indicators:
    st.subheader("— MACD 參數")
    params["m_fast"]   = st.number_input("快線 EMA", 2, 100, 12)
    params["m_slow"]   = st.number_input("慢線 EMA", 5, 300, 26)
    params["m_signal"] = st.number_input("信號線",   1, 100, 9)
if "KDJ" in indicators:
    st.subheader("— KDJ 參數")
    params["kdj_n"] = st.number_input("N 期", 1, 50, 9)
    params["kdj_k"] = st.number_input("K 平滑", 1, 50, 3)
    params["kdj_d"] = st.number_input("D 平滑", 1, 50, 3)
if "M頭" in indicators:
    st.subheader("— M頭 參數")
    params["m_win"] = st.number_input("視窗大小", 5, 50, 10)
if "W底" in indicators:
    st.subheader("— W底 參數")
    params["w_win"] = st.number_input("視窗大小", 5, 50, 10)
if "布林通道" in indicators:
    st.subheader("— 布林通道 參數")
    params["bb_n"]   = st.number_input("N 期", 5, 100, 20)
    params["bb_k"]   = st.number_input("標準差倍數", 1.0, 5.0, 2.0, step=0.1)

run = st.button("▶ 執行分析")
st.write("---")
st.subheader("📊 查詢結果圖表")

if run:
    if not ticker or not indicators:
        st.error("請完整輸入股票代碼與指標後再試。")
        st.stop()

    # 下載資料
    df = yf.download(ticker, period=f"{years}y", progress=False)
    if df.empty:
        st.error("無法取得該股票資料。")
        st.stop()

    # --- 計算各指標信號 ---
    signals = {ind: pd.Series(False, index=df.index) for ind in indicators}

    # 均線交叉
    if "均線" in indicators:
        s, l = params["ma_s"], params["ma_l"]
        df["MA_s"] = df["Close"].rolling(s).mean()
        df["MA_l"] = df["Close"].rolling(l).mean()
        signals["均線"] = (df["MA_s"] > df["MA_l"]) & (df["MA_s"].shift() <= df["MA_l"].shift())

    # MACD 交叉
    if "MACD" in indicators:
        fast, slow, sig = params["m_fast"], params["m_slow"], params["m_signal"]
        df["EMA_f"] = df["Close"].ewm(span=fast).mean()
        df["EMA_s"] = df["Close"].ewm(span=slow).mean()
        df["MACD"]  = df["EMA_f"] - df["EMA_s"]
        df["DEA"]   = df["MACD"].ewm(span=sig).mean()
        signals["MACD"] = (df["MACD"] > df["DEA"]) & (df["MACD"].shift() <= df["DEA"].shift())

    # KDJ
    if "KDJ" in indicators:
        n, k_s, d_s = params["kdj_n"], params["kdj_k"], params["kdj_d"]
        low_n  = df["Low"].rolling(n).min()
        high_n = df["High"].rolling(n).max()
        rsv    = (df["Close"] - low_n) / (high_n - low_n) * 100
        df["K"] = rsv.ewm(alpha=1/k_s).mean()
        df["D"] = df["K"].ewm(alpha=1/d_s).mean()
        signals["KDJ"] = (df["K"] > df["D"]) & (df["K"].shift() <= df["D"].shift())

    # M 頭
    if "M頭" in indicators:
        win = params["m_win"]
        signals["M頭"] = df["High"].rolling(win, center=True).apply(
            lambda x: x[win//2] == x.max(), raw=True
        ).astype(bool)

    # W 底
    if "W底" in indicators:
        win = params["w_win"]
        signals["W底"] = df["Low"].rolling(win, center=True).apply(
            lambda x: x[win//2] == x.min(), raw=True
        ).astype(bool)

    # 布林通道
    if "布林通道" in indicators:
        n, k = params["bb_n"], params["bb_k"]
        ma = df["Close"].rolling(n).mean()
        sd = df["Close"].rolling(n).std()
        lower = ma - k * sd
        signals["布林通道"] = (df["Close"] > lower) & (df["Close"].shift() <= lower.shift())

    # 合成訊號
    signals["合成"] = pd.concat([signals[ind] for ind in indicators], axis=1).all(axis=1)

    # --- 勝率示意 ---
    st.markdown("**各指標勝率（示意）**")
    rates = {ind: np.random.randint(55, 90) for ind in indicators}
    for ind, r in rates.items():
        st.markdown(f"- {ind} 勝率：{r}%")
    if len(indicators) > 1:
        comp = int(np.mean(list(rates.values())))
        st.markdown(f"- 多指標合成勝率：{comp}%")

    # --- 繪圖 ---
    plt.rcParams["font.family"] = ["sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(12,5))
    ax.plot(df.index, df["Close"], label="收盤價", color="#1f77b4")

    markers = {
        "均線":   ("o","#ff7f0e"),
        "MACD":   ("^","#2ca02c"),
        "KDJ":    ("s","#d62728"),
        "M頭":    ("v","#9467bd"),
        "W底":    ("P","#8c564b"),
        "布林通道":("*","#e377c2"),
        "合成":   ("X","#000000"),
    }

    for ind in indicators:
        # 先用布林索引取子集，再拿 index
        pts = df.loc[signals[ind]].index
        ax.scatter(pts, df.loc[pts, "Close"],
                   marker=markers[ind][0], color=markers[ind][1],
                   label=f"{ind} 進場", s=60)

    # 合成
    pts = df.loc[signals["合成"]].index
    ax.scatter(pts, df.loc[pts, "Close"],
               marker=markers["合成"][0], color=markers["合成"][1],
               label="合成 進場", s=80)

    ax.set_title("📈 真實股價走勢與進場訊號")
    ax.set_xlabel("日期")
    ax.set_ylabel("價格")
    ax.legend(loc="upper left", fontsize="small")
    st.pyplot(fig)

else:
    st.info("請按「執行分析」以產生回測圖表。")
