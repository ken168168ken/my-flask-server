import os
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# --- 1. Page config 必須放最前面 ---
st.set_page_config(
    page_title="K Technical Analysis",
    page_icon="logo.png",
)

# --- 2. Login ---
if 'GITHUB_USER' not in st.session_state:
    st.title("🔐 K 技術分析平台 登入")
    user = st.text_input("帳號", value=os.getenv("GITHUB_USER", ""), key="login_user")
    pwd  = st.text_input("密碼 (任意填)", type="password", key="login_pwd")
    if st.button("登入"):
        st.session_state.GITHUB_USER = user
        st.success("登入成功！請重新整理頁面或重新點擊「執行分析」。")
        st.stop()
    else:
        st.stop()

# --- 3. Main header + 圓形 Logo + 顯示帳號 ---
col1, col2 = st.columns([1, 9])
with col1:
    img = Image.open("logo.png").convert("RGBA")
    w, h = img.size
    circle = Image.new("L", (w, h), 0)
    import PIL.ImageDraw as D
    D.Draw(circle).ellipse((0, 0, w, h), fill=255)
    img.putalpha(circle)
    st.image(img, width=80)
with col2:
    st.markdown(
        f"<div style='text-align:right; font-size:14px;'>🔒 已登入帳號：`{st.session_state.GITHUB_USER}`</div>",
        unsafe_allow_html=True
    )

st.header("K 技術分析平台")
st.write("這是一個整合技術指標、回測模組、股票數據分析的平台。")

# --- 4. 查詢條件 & 參數 ---
st.subheader("✅ 查詢條件")
symbol = st.text_input("股票代碼 (例：2330.TW 或 AAPL)", "")
indicators = st.multiselect(
    "選擇技術指標",
    options=["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"],
)
years = st.slider("回測年限 (年)", 1, 3, 3)

# 參數區
params = {}
if "均線" in indicators:
    params["均線"] = st.number_input("SMA window", 1, 100, 20, key="p_sma")
if "MACD" in indicators:
    params["macd_fast"]   = st.number_input("MACD 快線 span", 1, 100, 12, key="p_macd_fast")
    params["macd_slow"]   = st.number_input("MACD 慢線 span", 1, 200, 26, key="p_macd_slow")
    params["macd_signal"] = st.number_input("MACD 信號線 span", 1, 50, 9, key="p_macd_sig")
if "KDJ" in indicators:
    params["kdj_n"] = st.number_input("KDJ 週期 N", 1, 50, 9, key="p_kdj_n")
    params["kdj_k"] = st.number_input("KDJ K 平滑", 1, 10, 3, key="p_kdj_k")
    params["kdj_d"] = st.number_input("KDJ D 平滑", 1, 10, 3, key="p_kdj_d")
if "M頭" in indicators:
    params["m_head"] = st.number_input("M-Head window", 1, 30, 10, key="p_mh")
if "W底" in indicators:
    params["w_bottom"] = st.number_input("W-Bottom window", 1, 30, 10, key="p_wb")
if "布林通道" in indicators:
    params["bb_period"] = st.number_input("BB 週期", 1, 100, 20, key="p_bb_p")
    params["bb_k"]      = st.number_input("BB 寬度 k", 0.1, 5.0, 2.0, step=0.1, key="p_bb_k")

# 必填欄位檢查
if not symbol or not indicators:
    st.info("請輸入股票代碼並至少選一個技術指標。")
    st.stop()

if st.button("執行分析"):
    # --- 5. 下載資料 ---
    end = pd.Timestamp.today()
    start = end - pd.DateOffset(years=years)
    df = yf.download(symbol, start=start, end=end)
    df.dropna(inplace=True)

    # --- 6. 計算 signals ---
    signals = {}
    # SMA
    if "均線" in indicators:
        sma = df["Close"].rolling(params["均線"]).mean()
        signals["均線"] = df["Close"] > sma
    # MACD
    if "MACD" in indicators:
        e1 = df["Close"].ewm(span=params["macd_fast"]).mean()
        e2 = df["Close"].ewm(span=params["macd_slow"]).mean()
        macd = e1 - e2
        sig  = macd.ewm(span=params["macd_signal"]).mean()
        signals["MACD"] = macd > sig
    # KDJ
    if "KDJ" in indicators:
        low_n  = df["Low"].rolling(params["kdj_n"]).min()
        high_n = df["High"].rolling(params["kdj_n"]).max()
        rsv    = 100 * (df["Close"] - low_n) / (high_n - low_n)
        k_val  = rsv.ewm(com=params["kdj_k"]-1).mean()
        d_val  = k_val.ewm(com=params["kdj_d"]-1).mean()
        j_val  = 3*k_val - 2*d_val
        signals["KDJ"] = (j_val > k_val) & (k_val > d_val)
    # M-Head / W-Bottom
    if "M頭" in indicators:
        signals["M頭"] = df["Close"] < df["Close"].shift(params["m_head"])
    if "W底" in indicators:
        signals["W底"] = df["Close"] > df["Close"].shift(params["w_bottom"])
    # Bollinger Bands
    if "布林通道" in indicators:
        mb = df["Close"].rolling(params["bb_period"]).mean()
        sd = df["Close"].rolling(params["bb_period"]).std()
        ub = mb + params["bb_k"] * sd
        lb = mb - params["bb_k"] * sd
        signals["布林通道"] = (df["Close"] < lb) | (df["Close"] > ub)
    # Combined
    if len(indicators) > 1:
        comb = pd.Series(True, index=df.index)
        for ind in indicators:
            comb = comb & signals[ind]
        signals["合成"] = comb

    # --- 7. 勝率列出 (英文 label) ---
    st.subheader("📊 各指標勝率")
    eng = {
        "均線": "SMA","MACD":"MACD","KDJ":"KDJ",
        "M頭":"M-Head","W底":"W-Bottom",
        "布林通道":"Bollinger Bands","合成":"Combined"
    }
    for ind, ser in signals.items():
        rate = int(ser.mean()*100)
        st.write(f"- {eng[ind]} 勝率：{rate}%")

    # --- 8. 圖表與進出場點 ---
    st.subheader("📈 Price & Entry Signals")
    markers = {
        "均線":   ("o","orange"),
        "MACD":  ("^","green"),
        "KDJ":   ("s","red"),
        "M頭":   ("v","purple"),
        "W底":   ("P","brown"),
        "布林通道":("*","pink"),
        "合成":   ("X","black"),
    }
    fig, ax = plt.subplots(figsize=(12,5))
    ax.plot(df.index, df["Close"], label="Close Price", color="blue")
    # 預先空 scatter 只留 legend
    for ind in signals:
        m, c = markers[ind]
        ax.scatter([],[], marker=m, color=c, label=eng[ind])
    # 真正畫點
    for ind, ser in signals.items():
        pts = ser[ser].index
        m, c = markers[ind]
        ax.scatter(pts, df.loc[pts,"Close"], marker=m, color=c, s=80)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    st.pyplot(fig, use_container_width=True)
