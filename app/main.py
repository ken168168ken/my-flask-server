# 主程式 main.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# 設定頁面標題
st.set_page_config(page_title="K 技術分析平台")
st.title("📊 K 技術分析平台")

# Session 狀態初始化（登入用）
if "user" not in st.session_state:
    st.session_state.user = None

# 登入畫面
if st.session_state.user is None:
    st.subheader("🔐 K 技術分析平台 登入")
    username = st.text_input("帳號")
    password = st.text_input("密碼（任意填）", type="password")
    if st.button("登入"):
        if username:
            st.session_state.user = username
            st.rerun()
        else:
            st.error("請輸入帳號！")
    st.stop()

# 登入成功畫面
st.markdown(f"<div style='text-align:right'>🔓 已登入：`{st.session_state.user}`</div>", unsafe_allow_html=True)

# ----------- 查詢參數區 -----------
st.subheader("✅ 查詢條件")
ticker = st.text_input("股票代碼 (例如：2330.TW 或 AAPL)", value="TSLA")

options = st.multiselect("選擇技術指標", ["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"], default=[])
years = st.slider("📆 回測年限 (年)", 1, 3, 1)

# 技術指標參數欄位
if "均線" in options:
    sma_short = st.number_input("SMA 短期 window", 1, 200, 10)
    sma_long = st.number_input("SMA 長期 window", 1, 200, 50)
    show_sma_cross = st.checkbox("顯示 SMA 金叉死叉點", value=True)

if "MACD" in options:
    macd_fast = st.number_input("MACD 快線 span", 1, 50, 12)
    macd_slow = st.number_input("MACD 慢線 span", 1, 50, 26)
    macd_signal = st.number_input("MACD 信號線 span", 1, 20, 9)
    show_macd_cross = st.checkbox("顯示 MACD 金叉死叉點", value=True)

if "KDJ" in options:
    k_period = st.number_input("KDJ K 週期", 1, 50, 9)
    d_period = st.number_input("KDJ D 週期", 1, 50, 3)
    j_period = st.number_input("KDJ J 週期", 1, 50, 3)

if "布林通道" in options:
    bb_period = st.number_input("BB 計算週期", 1, 50, 20)
    bb_width = st.number_input("BB 寬度倍率 (k)", 1.0, 5.0, 2.0)

if "M頭" in options:
    m_window = st.number_input("M 頭判斷區間長度", 5, 200, 10)

if "W底" in options:
    w_window = st.number_input("W 底判斷區間長度", 5, 200, 10)

# ----------- 按下分析按鈕後 -----------
if st.button("▶️ 執行分析"):
    try:
        df = yf.download(ticker, period=f"{years}y")
        df = df.reset_index()

        st.subheader("📈 各指標勝率")
        # 模擬回測勝率區塊（僅示意）
        win_rates = {
            "SMA": 50,
            "MACD": 52,
            "KDJ": 49,
            "M-Head": 47,
            "W-Bottom": 51,
            "Bollinger Bands": 12,
            "Combined": 66
        }
        for opt in options:
            label = {
                "均線": "SMA", "MACD": "MACD", "KDJ": "KDJ",
                "M頭": "M-Head", "W底": "W-Bottom", "布林通道": "Bollinger Bands"
            }[opt]
            st.markdown(f"- {label} 勝率：{win_rates[label]}%")

        if len(options) >= 2:
            st.markdown(f"- Combined 勝率：{win_rates['Combined']}%")

        # 畫圖顯示（用 Close 價）
        st.subheader("📉 價格與進出場點圖")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df["Date"], df["Close"], label="Close Price", linewidth=1)
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend(loc="upper left")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"錯誤：{e}")
