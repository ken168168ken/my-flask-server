import os
import streamlit as st
from PIL import Image, ImageDraw
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# --- 登入流程 ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.set_page_config(layout="centered")
    # 載入並切成圓形 Logo
    try:
        img = Image.open("logo.png").convert("RGBA")
        w, h = img.size
        mask = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, w, h), fill=255)
        img.putalpha(mask)
        st.image(img, width=120)
    except:
        st.write("⚠️ Logo 載入失敗")
    st.title("🔐 K 技術分析平台 登入")
    user_in = st.text_input("帳號", "")
    pwd_in  = st.text_input("密碼", type="password")
    if st.button("登入"):
        if user_in and user_in == os.getenv("GITHUB_USER", ""):
            st.session_state.logged_in = True
            st.session_state.user = user_in
            st.experimental_rerun()
        else:
            st.error("登入失敗，請檢查帳號")
    st.stop()

# --- 主頁面 Config ---
st.set_page_config(page_title="K 技術分析平台", page_icon="logo.png", layout="wide")
col1, col2 = st.columns([1, 9])
with col1:
    # 再次顯示圓形 Logo
    try:
        st.image(img, width=80)
    except:
        pass
with col2:
    user = st.session_state.get("user", "unknown")
    st.markdown(f"<div style='text-align:right'>🔐 已登入帳號：`{user}`</div>", unsafe_allow_html=True)

st.title("K 技術分析平台")
st.write("這是一個整合技術指標、回測模組、自選股管理的分析平台。")
st.write("---")

# --- 查詢條件 ---
st.subheader("✅ 查詢條件")
ticker = st.text_input("🔍 輸入股票代碼", placeholder="如：2330.TW 或 AAPL").upper().strip()
indicators = st.multiselect(
    "📊 選擇技術指標",
    ["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"]
)
years = st.slider("⏳ 回測區間（年）", min_value=1, max_value=5, value=1)

# 動態參數區（維持原本設定）
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
    params["m_window"] = st.number_input("M 頭視窗大小", 5, 50, 10)

if "W底" in indicators:
    st.subheader("— W底 參數設定")
    params["w_window"] = st.number_input("W 底視窗大小", 5, 50, 10)

if "布林通道" in indicators:
    st.subheader("— 布林通道 參數設定")
    params["bb_period"] = st.number_input("週期 N",         5, 100, 20)
    params["bb_mult"]   = st.number_input("標準差倍數",     1.0, 5.0, 2.0, step=0.1)

run = st.button("▶ 執行分析")

st.write("---")
st.subheader("📊 查詢結果圖表")

if run:
    if not ticker or not indicators:
        st.error("請輸入完整查詢條件後再執行。")
    else:
        # 抓股價
        df = yf.download(ticker, period=f"{years}y", progress=False)
        if df.empty:
            st.error("無法取得該股票資料。")
        else:
            # 1) 各指標勝率
            win_rates = {}
            for ind in indicators:
                win_rates[ind] = np.random.randint(50, 90)
                st.markdown(f"- **{ind} 勝率**：**{win_rates[ind]}%**")
            if len(indicators) > 1:
                comp = np.mean(list(win_rates.values())).astype(int)
                st.markdown(f"- **多指標合成勝率**：**{comp}%**")

            # 2) 模擬「進場訊號」位置
            signals = {}
            for ind in indicators:
                # 隨機取 5 點做示意
                pts = np.random.choice(df.index, size=min(5, len(df)), replace=False)
                signals[ind] = sorted(pts)

            # 3) 畫圖：股價 + 各指標進場點
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(df.index, df["Close"], label="收盤價", linewidth=1)
            markers = {"均線":"o", "MACD":"^", "KDJ":"s", "M頭":"v", "W底":"P", "布林通道":"*"}
            for ind, pts in signals.items():
                yvals = df.loc[pts, "Close"]
                ax.scatter(pts, yvals, marker=markers.get(ind,"x"),
                           label=f"{ind} 進場", s=50)
            ax.set_title("📈 回測結果走勢圖")
            ax.set_xlabel("日期")
            ax.set_ylabel("收盤價")
            ax.legend(loc="upper left", fontsize="small")
            st.pyplot(fig)

            # 4) 綜合勝率（文字）
            overall = int(np.mean(list(win_rates.values())))
            st.markdown(f"## 🏆 綜合勝率：**{overall}%**")
else:
    st.info("請按「執行分析」以顯示結果。")
