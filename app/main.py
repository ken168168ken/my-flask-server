import os
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

# — 登录流程（同前） —
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    try:
        raw = Image.open("logo.png").convert("RGBA")
        w,h = raw.size
        mask = Image.new("L",(w,h),0)
        ImageDraw.Draw(mask).ellipse((0,0,w,h),fill=255)
        raw.putalpha(mask)
        st.image(raw, width=120)
    except:
        st.warning("⚠️ 載入 logo 失敗")

    st.title("🔐 K 技術分析平台 登入")
    with st.form("login_form"):
        user_in = st.text_input("帳號", "")
        pwd_in  = st.text_input("密碼 (任意填)", type="password")
        if st.form_submit_button("登入"):
            if user_in and user_in == os.getenv("GITHUB_USER", ""):
                st.session_state.logged_in = True
            else:
                st.error("登入失敗，請檢查帳號或環境變數")
    if not st.session_state.logged_in:
        st.stop()

# — 主頁 Header 同前 —
st.set_page_config(page_title="K 技術分析平台", page_icon="logo.png", layout="wide")
col1, col2 = st.columns([1,9])
with col1:
    try: st.image(raw, width=80)
    except: pass
with col2:
    st.markdown(f"<div style='text-align:right'>🔐 已登入：`{st.session_state.GITHUB_USER}`</div>",
                unsafe_allow_html=True)

st.title("K 技術分析平台")
st.write("---")

# — 查詢條件 同前 —
st.subheader("✅ 查詢條件")
ticker = st.text_input("🔍 股票代碼 (例：2330.TW 或 AAPL)", "").upper().strip()
inds   = st.multiselect("📊 選擇技術指標",
                        ["均線","MACD","KDJ","M頭","W底","布林通道"])
years  = st.slider("⏳ 回測年限", 1, 5, 1)
run    = st.button("▶ 執行分析")

if run:
    if not ticker or not inds:
        st.error("請完整填寫「股票代碼」與「技術指標」")
        st.stop()

    df = yf.download(ticker, period=f"{years}y", progress=False)
    if df.empty:
        st.error("無法取得該股票資料")
        st.stop()

    # 生成 signals
    signals = {ind: pd.Series(False, index=df.index) for ind in inds}
    # 範例：M 頭 / W 底 / 布林通道
    if "M頭" in inds:
        win = 10
        signals["M頭"] = (
            df["High"].rolling(win, center=True)
               .apply(lambda x: x[win//2]==x.max(), raw=True)
               .astype(bool)
        )
    if "W底" in inds:
        win = 10
        signals["W底"] = (
            df["Low"].rolling(win, center=True)
              .apply(lambda x: x[win//2]==x.min(), raw=True)
              .astype(bool)
        )
    if "布林通道" in inds:
        n,k=20,2
        ma = df["Close"].rolling(n).mean()
        sd = df["Close"].rolling(n).std()
        lower = ma - k*sd
        signals["布林通道"] = (df["Close"]>lower)&(df["Close"].shift()<=lower.shift())

    # 多指標合成
    if len(inds)>1:
        signals["合成"] = pd.concat([signals[i] for i in inds], axis=1).all(axis=1)

    # 顯示文字勝率（示意）
    st.markdown("**各指標勝率（示意）**")
    rates = {i: np.random.randint(55,90) for i in inds}
    for i,r in rates.items():
        st.markdown(f"- {i} 勝率：{r}%")
    if "合成" in signals:
        st.markdown(f"- 多指標合成勝率：{int(np.mean(list(rates.values())))}%")

    # 畫圖，用英文標籤
    st.subheader("📈 Price & Entry Signals")
    fig, ax = plt.subplots(figsize=(12,5))
    ax.plot(df.index, df["Close"], label="Close Price")

    # 先空 scatter 讓 legend 出現所有指標
    markers = {
        "均線":("o","orange"),
        "MACD":("^","green"),
        "KDJ":("s","red"),
        "M頭":("v","purple"),
        "W底":("P","brown"),
        "布林通道":("*","pink"),
        "合成":("X","black"),
    }
    for ind in signals.keys():
        ax.scatter([], [], marker=markers[ind][0],
                   color=markers[ind][1], label=f"{ind}")

    # 真正進場點
    for ind,ser in signals.items():
        pts = df.loc[ser].index
        ax.scatter(pts, df.loc[pts,"Close"],
                   marker=markers[ind][0],
                   color=markers[ind][1],
                   s=80)

    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    st.pyplot(fig)
