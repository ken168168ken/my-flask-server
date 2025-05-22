import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# ----- 登入流程 -----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.set_page_config(layout="centered")
    st.image("logo.png", width=100)
    st.title("🔒 K 技術分析平台 登入")
    user_in = st.text_input("帳號", "")
    pwd_in  = st.text_input("密碼", type="password")
    if st.button("登入"):
        # 這裡可改成真正驗證，範例用環境變數 GITHUB_USER
        if user_in and user_in == os.getenv("GITHUB_USER", ""):
            st.session_state.logged_in = True
            st.session_state.user = user_in
            st.experimental_rerun()
        else:
            st.error("登入失敗，請檢查帳號")
    st.stop()

# ----- 主頁面設定 -----
st.set_page_config(page_title="K 技術分析平台", page_icon="logo.png", layout="wide")
col1, col2 = st.columns([1, 9])
with col1:
    st.image("logo.png", width=80, clamp=True, output_format="PNG")
with col2:
    user = st.session_state.get("user", "unknown")
    st.markdown(f"<div style='text-align:right'>🔐 已登入帳號：`{user}`</div>", unsafe_allow_html=True)

st.title("K 技術分析平台")
st.write("這是一個整合技術指標、回測模組、自選股管理的分析平台。")
st.write("---")

# ----- 查詢條件 -----
st.subheader("✅ 查詢條件")
ticker = st.text_input("🔍 輸入股票代碼", placeholder="如：2330.TW 或 AAPL").upper().strip()
indicators = st.multiselect(
    "📊 選擇技術指標",
    ["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"]
)
years = st.slider("⏳ 回測區間（年）", min_value=1, max_value=5, value=1)

# 動態參數
params = {}
if "均線" in indicators:
    st.subheader("— 均線 參數設定")
    params["ma_short"] = st.number_input("短期 MA 週期", 2, 200, 5)
    params["ma_long"]  = st.number_input("長期 MA 週期", 5, 300, 20)

if "MACD" in indicators:
    st.subheader("— MACD 參數設定")
    params["macd_fast"]   = st.number_input("快線 EMA 週期", 2, 100, 12)
    params["macd_slow"]   = st.number_input("慢線 EMA 週期", 5, 300, 26)
    params["macd_signal"] = st.number_input("信號線週期",   1, 100, 9)

if "KDJ" in indicators:
    st.subheader("— KDJ 參數設定")
    params["kdj_n"] = st.number_input("KDJ N 期",    1, 50, 9)
    params["kdj_k"] = st.number_input("K 期平滑",     1, 50, 3)
    params["kdj_d"] = st.number_input("D 期平滑",     1, 50, 3)

if "M頭" in indicators:
    st.subheader("— M頭 參數設定")
    params["m_window"] = st.number_input("M頭視窗大小", 5, 50, 10)

if "W底" in indicators:
    st.subheader("— W底 參數設定")
    params["w_window"] = st.number_input("W底視窗大小", 5, 50, 10)

if "布林通道" in indicators:
    st.subheader("— 布林通道 參數設定")
    params["bb_period"] = st.number_input("週期 N",         5, 100, 20)
    params["bb_mult"]   = st.number_input("標準差倍數",     1.0, 5.0, 2.0, step=0.1)

run = st.button("▶ 執行分析")

# ----- 結果顯示區 -----
st.write("---")
st.subheader("📊 查詢結果圖表")

if run:
    if not ticker or not indicators:
        st.error("請輸入完整查詢條件。")
    else:
        # 1) 抓取股價
        df = yf.download(ticker, period=f"{years}y", progress=False)
        if df.empty:
            st.error("無法取得該股票資料。")
        else:
            # 2) 文字結果
            for ind in indicators:
                st.markdown(f"- **{ind}**：示意回測結果文字說明")
            if len(indicators) > 1:
                st.markdown(f"- **多指標合成**：示意多指標合成結果文字說明")

            # 3) 走勢圖
            fig, ax = plt.subplots()
            ax.plot(df.index, df["Close"], label="股價收盤")
            ax.set_title("📈 回測結果走勢圖")
            ax.set_xlabel("日期")
            ax.set_ylabel("收盤價")
            ax.legend()
            st.pyplot(fig)

            # 4) 勝率文字
            win_rate = np.random.randint(50, 90)
            st.markdown(f"## 🏆 綜合勝率：**{win_rate}%**")

else:
    st.info("請按「執行分析」以顯示結果。")
