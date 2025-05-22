import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 頂部 Logo 與使用者帳號 ---
st.set_page_config(page_title="K 技術分析平台", page_icon="logo.png", layout="wide")
col1, col2 = st.columns([1, 9])
with col1:
    try:
        img = Image.open("logo.png")
        st.image(img, width=80)
    except:
        st.write("❗Logo 載入失敗")
with col2:
    st.markdown(
        "<div style='text-align: right; font-size:14px;'>"
        "🔒 已登入帳號：`{}`".format(st.secrets["GITHUB_USER"]) +
        "（主帳號） | 模式：`PRO`</div>",
        unsafe_allow_html=True
    )

st.title("K 技術分析平台")
st.write("這是一個整合技術指標、回測模組、自選股管理的分析平台。")
st.write("---")

# --- 查詢條件區 ---
st.header("✅ 查詢條件")
symbol = st.text_input("🔍 輸入股票代碼", placeholder="如：2330.TW 或 AAPL")
indicators = st.multiselect(
    "📊 選擇技術指標",
    ["均線", "MACD", "KDJ", "RSI"]
)
period = st.slider("⏳ 回測區間（年）", min_value=1, max_value=5, value=1)

# --- 動態參數輸入 ---
st.write("---")
param_cols = {}
for ind in indicators:
    if ind == "均線":
        st.subheader("— 均線期間設定")
        param_cols["ma_short"] = st.number_input("一均線短期週期", min_value=1, value=5)
        param_cols["ma_long"]  = st.number_input("一均線長期週期", min_value=1, value=20)
    if ind == "MACD":
        st.subheader("— MACD 參數設定")
        param_cols["macd_fast"]   = st.number_input("MACD 快線 EMA 週期", min_value=1, value=12)
        param_cols["macd_slow"]   = st.number_input("MACD 慢線 EMA 週期", min_value=1, value=26)
        param_cols["macd_signal"] = st.number_input("MACD 信號線週期", min_value=1, value=9)
    if ind == "KDJ":
        st.subheader("— KDJ 參數設定")
        param_cols["kdj_rsv"] = st.number_input("KDJ RSV 週期", min_value=1, value=9)
        param_cols["kdj_k"]   = st.number_input("KDJ K 線週期", min_value=1, value=3)
        param_cols["kdj_d"]   = st.number_input("KDJ D 線週期", min_value=1, value=3)
    if ind == "RSI":
        st.subheader("— RSI 參數設定")
        param_cols["rsi_period"] = st.number_input("RSI 週期", min_value=1, value=14)

# --- 執行分析按鈕 ---
st.write("---")
if st.button("▶️ 執行分析"):
    if not symbol or not indicators:
        st.error("請先輸入股票代碼並至少選擇一個技術指標！")
    else:
        # 示意用隨機數據，實際請串後端回測
        np.random.seed(42)
        x = np.linspace(0, period, 10)
        y = np.random.randint(1, 6, size=10)
        fig, ax = plt.subplots()
        ax.plot(x, y, marker="o")
        ax.set_title("回測結果走勢圖")
        ax.set_xlabel("年")
        ax.set_ylabel("指標值")
        st.pyplot(fig)

        # 綜合勝率文字顯示
        win_rate = np.random.randint(50, 100)  # 示意
        st.markdown(f"🏆 **綜合勝率：{win_rate}%**")

# --- 查詢結果圖表預留區 ---
st.write("---")
st.header("📈 查詢結果圖表")
st.info("這裡將顯示股價走勢與技術指標圖。")  
