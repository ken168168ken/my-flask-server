import os
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

# ───────────────────────────────
# 1. 一定要最先呼叫
st.set_page_config(page_title="K 技術分析平台", page_icon="logo.png", layout="wide")

# 2. session_state 初始化
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "GITHUB_USER" not in st.session_state:
    st.session_state.GITHUB_USER = ""

# ───────────────────────────────
# 3. 登入流程（不再用 experimental_rerun）
if not st.session_state.logged_in:
    # 圓形 logo
    try:
        raw = Image.open("logo.png").convert("RGBA")
        w, h = raw.size
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, w, h), fill=255)
        raw.putalpha(mask)
        st.image(raw, width=120)
    except:
        st.warning("⚠️ 載入 logo 失敗")

    st.title("🔐 K 技術分析平台 登入")
    with st.form("login_form"):
        user_in = st.text_input("帳號", "")
        pwd_in  = st.text_input("密碼 (任意填)", type="password")
        ok = st.form_submit_button("登入")
        if ok:
            env_user = os.getenv("GITHUB_USER", "")
            if user_in and user_in == env_user:
                st.session_state.logged_in = True
            else:
                st.error("登入失敗，請檢查帳號或環境變數")

    st.stop()

# ───────────────────────────────
# 4. 已登入後主畫面 Header
col1, col2 = st.columns([1, 9])
with col1:
    try:
        st.image(raw, width=80)
    except:
        pass
with col2:
    st.markdown(
        f"<div style='text-align:right'>🔐 已登入：`{st.session_state.GITHUB_USER}`</div>",
        unsafe_allow_html=True
    )

st.title("K 技術分析平台")
st.write("---")

# ───────────────────────────────
# 5. 查詢條件：回測年限改為 1–3 年
st.subheader("✅ 查詢條件")
ticker = st.text_input("🔍 股票代碼 (例：2330.TW 或 AAPL)", "").upper().strip()
inds   = st.multiselect("📊 選擇技術指標",
                        ["均線","MACD","KDJ","M頭","W底","布林通道"])
years  = st.slider("⏳ 回測年限 (年)", 1, 3, 1)  # 改成最多 3 年
run    = st.button("▶ 執行分析")

if run:
    if not ticker or not inds:
        st.error("請完整填寫「股票代碼」與「技術指標」")
        st.stop()

    # 下載股價
    df = yf.download(ticker, period=f"{years}y", progress=False)
    if df.empty:
        st.error("無法取得該股票資料")
        st.stop()

    # 產生 signals
    signals = {}
    for ind in inds:
        signals[ind] = pd.Series(False, index=df.index)

    # M 頭
    if "M頭" in inds:
        win = st.number_input("M 頭 window", 5, 30, 10, key="m_head")
        signals["M頭"] = (
            df["High"].rolling(win, center=True)
               .apply(lambda x: x[win//2]==x.max(), raw=True)
               .astype(bool)
        )

    # W 底
    if "W底" in inds:
        win = st.number_input("W 底 window", 5, 30, 10, key="w_walk")
        signals["W底"] = (
            df["Low"].rolling(win, center=True)
              .apply(lambda x: x[win//2]==x.min(), raw=True)
              .astype(bool)
        )

    # 布林通道
    if "布林通道" in inds:
        n = st.number_input("BB period", 5, 60, 20, key="bb_n")
        k = st.slider("BB width (k)", 1, 3, 2, key="bb_k")
        ma    = df["Close"].rolling(n).mean()
        sd    = df["Close"].rolling(n).std()
        lower = ma - k*sd
        signals["布林通道"] = (df["Close"] > lower) & (df["Close"].shift() <= lower.shift())

    # 多指標合成
    if len(inds) > 1:
        combined = pd.concat([signals[i] for i in inds], axis=1).all(axis=1)
        signals["合成"] = combined

    # 顯示勝率（示意）
    st.markdown("**各指標勝率（示意）**")
    rates = {i: np.random.randint(55, 90) for i in signals}
    for i, r in rates.items():
        st.markdown(f"- {i} 勝率：{r}%")

    # 價格走勢 & 進場點
    st.subheader("📈 Price & Entry Signals")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df.index, df["Close"], label="Close Price")
    markers = {
        "均線":("o","orange"),
        "MACD":("^","green"),
        "KDJ":("s","red"),
        "M頭":("v","purple"),
        "W底":("P","brown"),
        "布林通道":("*","pink"),
        "合成":("X","black"),
    }

    # 先畫空的 scatter 以便 legend
    for ind in signals:
        ax.scatter([], [], marker=markers[ind][0],
                   color=markers[ind][1], label=ind)

    # 真正的進場點
    for ind, ser in signals.items():
        idx = ser[ser].index  # 這裡保證 ser 一定是 Series
        ax.scatter(idx, df.loc[idx, "Close"],
                   marker=markers[ind][0],
                   color=markers[ind][1], s=80)

    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")

    # 這行讓圖表能正確顯示
    st.pyplot(fig, use_container_width=True)
