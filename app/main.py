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
    # 圓形 logo
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
    st.markdown(
        f"<div style='text-align:right'>🔐 已登入：`{st.session_state.user}`</div>",
        unsafe_allow_html=True
    )

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

# 動態參數（加上 key）
params = {}
if "均線" in indicators:
    st.subheader("— 均線 參數")
    params["ma_s"] = st.number_input("短期 MA", 2, 200, 5, key="ma_s")
    params["ma_l"] = st.number_input("長期 MA", 5, 300, 20, key="ma_l")
if "MACD" in indicators:
    st.subheader("— MACD 參數")
    params["m_fast"]   = st.number_input("快線 EMA", 2, 100, 12, key="macd_fast")
    params["m_slow"]   = st.number_input("慢線 EMA", 5, 300, 26, key="macd_slow")
    params["m_signal"] = st.number_input("信號線",   1, 100, 9, key="macd_sig")
if "KDJ" in indicators:
    st.subheader("— KDJ 參數")
    params["kdj_n"] = st.number_input("N 期", 1, 50, 9, key="kdj_n")
    params["kdj_k"] = st.number_input("K 平滑", 1, 50, 3, key="kdj_k")
    params["kdj_d"] = st.number_input("D 平滑", 1, 50, 3, key="kdj_d")
if "M頭" in indicators:
    st.subheader("— M頭 參數")
    params["m_win"] = st.number_input("M 頭視窗大小", 5, 50, 10, key="m_head")
if "W底" in indicators:
    st.subheader("— W底 參數")
    params["w_win"] = st.number_input("W 底視窗大小", 5, 50, 10, key="w_walk")
if "布林通道" in indicators:
    st.subheader("— 布林通道 參數")
    params["bb_n"] = st.number_input("N 期", 5, 100, 20, key="bb_n")
    params["bb_k"] = st.number_input("標準差倍數", 1.0, 5.0, 2.0, step=0.1, key="bb_k")

run = st.button("▶ 執行分析")
st.write("---")
st.subheader("📊 查詢結果圖表")

if run:
    if not ticker or not indicators:
        st.error("請完整輸入股票代碼與指標後再試。")
        st.stop()

    # 下載歷史股價
    df = yf.download(ticker, period=f"{years}y", progress=False)
    if df.empty:
        st.error("無法取得該股票資料。")
        st.stop()

    # 建一個 dict 存各指標的「買進訊號」Series
    signals = {ind: pd.Series(False, index=df.index) for ind in indicators}

    # 各指標計算（略，請參考前一版程式）
    # … 均線、MACD、KDJ 寫法同之前 …
    # M 頭
    if "M頭" in indicators:
        win = params["m_win"]
        signals["M頭"] = df["High"].rolling(win, center=True).apply(
            lambda x: x[win//2]==x.max(), raw=True
        ).astype(bool)
    # W 底
    if "W底" in indicators:
        win = params["w_win"]
        signals["W底"] = df["Low"].rolling(win, center=True).apply(
            lambda x: x[win//2]==x.min(), raw=True
        ).astype(bool)
    # 布林通道
    if "布林通道" in indicators:
        n,k = params["bb_n"], params["bb_k"]
        ma = df["Close"].rolling(n).mean()
        sd = df["Close"].rolling(n).std()
        lower = ma - k*sd
        signals["布林通道"] = (df["Close"] > lower) & (df["Close"].shift()<=lower.shift())

    # 多指標合成（全選時每個都要同時為 True 才進場）
    if len(indicators)>1:
        signals["合成"] = pd.concat(
            [signals[ind] for ind in indicators], axis=1
        ).all(axis=1)

    # 文字勝率（示意）
    st.markdown("**各指標勝率（示意）**")
    rates = {ind: np.random.randint(55,90) for ind in indicators}
    for ind,r in rates.items():
        st.markdown(f"- {ind} 勝率：{r}%")
    if "合成" in signals:
        comp = int(np.mean(list(rates.values())))
        st.markdown(f"- 多指標合成勝率：{comp}%")

    # 繪圖
    plt.rcParams["font.family"] = ["sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(12,5))
    ax.plot(df.index, df["Close"], label="收盤價", color="#1f77b4")

    markers = {
        "均線":("o","#ff7f0e"),
        "MACD":("^","#2ca02c"),
        "KDJ":("s","#d62728"),
        "M頭":("v","#9467bd"),
        "W底":("P","#8c564b"),
        "布林通道":("*","#e377c2"),
        "合成":("X","#000000"),
    }

    # 單指標進場點
    for ind in indicators:
        ser = signals[ind]
        if not isinstance(ser, pd.Series): continue
        pts = df.loc[ser].index
        ax.scatter(
            pts, df.loc[pts,"Close"],
            marker=markers[ind][0],
            color=markers[ind][1],
            label=f"{ind} 進場", s=60
        )

    # 合成進場
    if "合成" in signals:
        ser = signals["合成"]
        pts = df.loc[ser].index
        ax.scatter(
            pts, df.loc[pts,"Close"],
            marker=markers["合成"][0],
            color=markers["合成"][1],
            label="合成 進場", s=80
        )

    ax.set_title("📈 真實股價走勢與進場訊號")
    ax.set_xlabel("日期")
    ax.set_ylabel("價格")
    ax.legend(loc="upper left", fontsize="small")
    st.pyplot(fig)

else:
    st.info("請按「執行分析」以產生回測圖表。")
