import os
import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# 1. Page config (最前面)
st.set_page_config(
    page_title="K Technical Analysis",
    page_icon="logo.png",
)

# 2. Login 
if 'GITHUB_USER' not in st.session_state:
    st.title("🔐 K 技術分析平台 登入")
    user = st.text_input("帳號", value=os.getenv("GITHUB_USER", ""), key="login_user")
    pwd  = st.text_input("密碼 (任意填)", type="password", key="login_pwd")
    if st.button("登入"):
        st.session_state.GITHUB_USER = user
        st.success("登入成功！請重新整理或重新點選「執行分析」。")
        st.stop()
    else:
        st.stop()

# 3. Header + 圓形 Logo + 顯示帳號
col1, col2 = st.columns([1, 9])
with col1:
    img = Image.open("logo.png").convert("RGBA")
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    import PIL.ImageDraw as D
    D.Draw(mask).ellipse((0, 0, w, h), fill=255)
    img.putalpha(mask)
    st.image(img, width=80)
with col2:
    st.markdown(
        f"<div style='text-align:right; font-size:14px;'>🔒 已登入帳號：`{st.session_state.GITHUB_USER}`</div>",
        unsafe_allow_html=True
    )

st.header("K 技術分析平台")
st.write("整合技術指標、回測模組、股票數據分析的平台。")

# 4. 條件輸入
st.subheader("✅ 查詢條件")
symbol = st.text_input("股票代碼 (例：2330.TW 或 AAPL)", "")
inds   = st.multiselect(
    "選擇技術指標",
    ["均線","MACD","KDJ","M頭","W底","布林通道"]
)
years = st.slider("回測年限 (年)", 1, 3, 3)

# 參數區
params = {}
if "均線" in inds:
    params["sma_short"] = st.number_input("SMA 短期 window", 1, 100, 10, key="p_s_s")
    params["sma_long"]  = st.number_input("SMA 長期 window", 1, 200, 50, key="p_s_l")
if "MACD" in inds:
    params["macd_fast"]   = st.number_input("MACD 快線 span", 1, 100, 12, key="p_f")
    params["macd_slow"]   = st.number_input("MACD 慢線 span", 1, 200, 26, key="p_s")
    params["macd_signal"] = st.number_input("MACD 信號線 span", 1, 50, 9, key="p_sig")
# ...（其餘 KDJ、M頭、W底、布林同之前）

if not symbol or not inds:
    st.info("請輸入股票代碼並至少選一個技術指標。")
    st.stop()

if st.button("執行分析"):
    # 5. 下載資料
    end   = pd.Timestamp.today()
    start = end - pd.DateOffset(years=years)
    df = yf.download(symbol, start=start, end=end).dropna()

    # 6. signals
    signals = {}
    # SMA 金叉
    if "均線" in inds:
        ma_s = df["Close"].rolling(params["sma_short"]).mean()
        ma_l = df["Close"].rolling(params["sma_long"]).mean()
        cross = (ma_s > ma_l) & (ma_s.shift() <= ma_l.shift())
        signals["均線"] = cross
    # MACD…
    # KDJ…
    # M頭 / W底…
    # 布林…
    # Combined
    if len(inds) > 1:
        comb = pd.Series(True, index=df.index)
        for ind in signals:
            comb = comb & signals[ind]
        signals["合成"] = comb

    # 7. 勝率（用 float() 再 int()）
    st.subheader("📊 各指標勝率")
    eng = {
        "均線":"SMA","MACD":"MACD","KDJ":"KDJ",
        "M頭":"M-Head","W底":"W-Bottom",
        "布林通道":"Bollinger Bands","合成":"Combined"
    }
    for ind, ser in signals.items():
        rate = int(float(ser.mean()) * 100)
        st.write(f"- {eng[ind]} 勝率：{rate}%")

    # 8. 圖表 + 進場點
    st.subheader("📈 Price & Entry Signals")
    markers = {
        "均線":("o","orange"),"MACD":("^","green"),"KDJ":("s","red"),
        "M頭":("v","purple"),"W底":("P","brown"),"布林通道":("*","pink"),
        "合成":("X","black")
    }
    fig, ax = plt.subplots(figsize=(12,5))
    ax.plot(df.index, df["Close"], label="Close Price", color="blue")
    # 先留 legend
    for ind in signals:
        m,c = markers[ind]
        ax.scatter([],[], marker=m, c=c, label=eng[ind])
    # 實際進場點
    for ind, ser in signals.items():
        pts = ser[ser].index
        m,c = markers[ind]
        ax.scatter(pts, df.loc[pts,"Close"], marker=m, c=c, s=80)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    st.pyplot(fig, use_container_width=True)
