import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 頁面設定(Logo+標題) ---
st.set_page_config(
    page_title="K 技術分析平台",
    page_icon="logo.png",
    layout="wide"
)

# 上方兩欄：Logo (圓形) ＋ 已登入帳號
col1, col2 = st.columns([1, 9])
with col1:
    st.markdown(
        "<img src='logo.png' style='border-radius:50%; width:80px;'/>",
        unsafe_allow_html=True
    )
with col2:
    github_user = os.getenv("GITHUB_USER", "unknown")
    st.markdown(
        f"<div style='text-align: right; font-size:14px;'>🔐 已登入帳號：`{github_user}`</div>",
        unsafe_allow_html=True
    )

# 標題
st.title("K 技術分析平台")
st.write("這是一個整合技術指標、回測模組、自選股管理的分析平台。")
st.write("---")

# --- 查詢條件 ---
st.subheader("✅ 查詢條件")
ticker = st.text_input("🔍 輸入股票代碼", placeholder="如：2330.TW 或 AAPL")
indicators = st.multiselect(
    "📊 選擇技術指標",
    ["均線", "MACD", "KDJ", "M頭W底", "布林通道"]
)
years = st.slider("⏳ 回測區間（年）", min_value=1, max_value=5, value=1)

# 動態參數區
params = {}
if "均線" in indicators:
    st.subheader("— 均線參數設定")
    params["ma_short"] = st.number_input("短期週期", 2, 200, 5)
    params["ma_long"]  = st.number_input("長期週期", 5, 300, 20)

if "MACD" in indicators:
    st.subheader("— MACD 參數設定")
    params["macd_fast"]   = st.number_input("快線 EMA 週期",    2, 100, 12)
    params["macd_slow"]   = st.number_input("慢線 EMA 週期",    5, 300, 26)
    params["macd_signal"] = st.number_input("信號線週期",      1, 100, 9)

if "KDJ" in indicators:
    st.subheader("— KDJ 參數設定")
    params["kdj_n"] = st.number_input("KDJ N 期",    1, 50, 9)
    params["kdj_k"] = st.number_input("K 期平滑",     1, 50, 3)
    params["kdj_d"] = st.number_input("D 期平滑",     1, 50, 3)

if "M頭W底" in indicators:
    st.subheader("— M頭W底 參數設定")
    params["mw_window"] = st.number_input("判定視窗大小", 5, 50, 10)

if "布林通道" in indicators:
    st.subheader("— 布林通道 參數設定")
    params["bb_period"]    = st.number_input("週期 N",           5, 100, 20)
    params["bb_mult"]      = st.number_input("標準差倍數",       1.0, 5.0, 2.0, step=0.1)

# 執行分析按鈕
analyzed = False
if st.button("▶ 執行分析"):
    if not ticker or not indicators:
        st.error("請輸入股票代碼並至少選擇一項技術指標。")
    else:
        analyzed = True
        st.success("分析完成！")

# --- 查詢結果圖表區（一定出現在最下面） ---
st.write("---")
st.subheader("📊 查詢結果圖表")

if analyzed:
    # 1) 純文字示意結果
    for ind in indicators:
        st.markdown(f"- **{ind}**：示意回測結果文字說明")

    # 2) 回測走勢圖 (示意)
    x = np.linspace(0, years, years * 10 + 1)
    y = np.sin(x) + np.random.randn(len(x)) * 0.1 + 3
    fig, ax = plt.subplots()
    ax.plot(x, y, marker="o")
    ax.set_title("📈 回測結果走勢圖")
    ax.set_xlabel("時間 (年)")
    ax.set_ylabel("指標值")
    st.pyplot(fig)

    # 3) 純文字勝率
    win_rate = np.random.randint(50, 90)
    st.markdown(f"## 🏆 綜合勝率：**{win_rate}%**")
else:
    st.info("請按「執行分析」以顯示結果。")
