import os
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 頁面設定(Logo+標題) ---
st.set_page_config(
    page_title="K 技術分析平台",
    page_icon="logo.png",
    layout="wide"
)

# 上方兩欄：Logo ＋ 已登入帳號
col1, col2 = st.columns([1, 9])
with col1:
    try:
        img = Image.open("logo.png")
        st.image(img, width=80)
    except FileNotFoundError:
        st.write("⚠ Logo 載入失敗")

with col2:
    github_user = os.getenv("GITHUB_USER", "unknown")
    st.markdown(
        f"<div style='text-align: right; font-size:14px;'>🔐 已登入帳號：`{github_user}`</div>",
        unsafe_allow_html=True
    )

st.title("K 技術分析平台")
st.write("這是一個整合技術指標、回測模組、自選股管理的分析平台。")
st.write("---")

# --- 查詢條件 ---
st.subheader("✅ 查詢條件")
ticker = st.text_input("🔍 輸入股票代碼", placeholder="如：2330.TW 或 AAPL")
indicators = st.multiselect("📊 選擇技術指標", ["均線", "MACD", "KDJ"])
years = st.slider("⏳ 回測區間（年）", 1, 5, 1)

# --- 動態參數區 ---
params = {}
if "均線" in indicators:
    st.subheader("— 均線參數設定")
    params["ma_short"] = st.number_input("短期週期", min_value=2, max_value=200, value=5)
    params["ma_long"] = st.number_input("長期週期", min_value=5, max_value=300, value=20)

if "MACD" in indicators:
    st.subheader("— MACD 參數設定")
    params["macd_fast"] = st.number_input("快線 EMA 週期", min_value=2, max_value=100, value=12)
    params["macd_slow"] = st.number_input("慢線 EMA 週期", min_value=5, max_value=300, value=26)
    params["macd_signal"] = st.number_input("信號線週期", min_value=1, max_value=100, value=9)

if "KDJ" in indicators:
    st.subheader("— KDJ 參數設定")
    params["kdj_n"] = st.number_input("KDJ N 期", min_value=1, max_value=50, value=9)
    params["kdj_k"] = st.number_input("K 期平滑", min_value=1, max_value=50, value=3)
    params["kdj_d"] = st.number_input("D 期平滑", min_value=1, max_value=50, value=3)

# --- 執行分析按鈕 ---
if st.button("▶ 執行分析"):
    if not ticker or not indicators:
        st.error("請輸入股票代碼並至少選擇一項技術指標。")
    else:
        st.success("分析完成！")

        # 示意用：隨機產生一條回測線
        x = np.linspace(0, years, num=years*10+1)
        y = np.sin(x) + np.random.randn(len(x))*0.1 + 3

        fig, ax = plt.subplots()
        ax.plot(x, y, marker="o")
        ax.set_title("📈 回測結果走勢圖")
        ax.set_xlabel("時間 (年)")
        ax.set_ylabel("示意指標值")
        st.pyplot(fig)

        # 示意勝率
        win_rate = np.random.randint(50, 90)
        st.markdown(f"## 🏆 綜合勝率：**{win_rate}%**")

# --- 查詢結果圖表區 (預留) ---
st.write("---")
st.subheader("📊 查詢結果圖表")
st.info("這裡將顯示股價走勢與技術指標圖。")
