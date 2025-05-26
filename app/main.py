import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime

# ---------- LOGO 顯示 ----------
LOGO_URL = "https://raw.githubusercontent.com/ken168168ken/my-flask-server/main/logo.png"

# ---------- 登入狀態初始化 ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------- 登入頁面 ----------
if not st.session_state.logged_in:
    st.image(LOGO_URL, width=100)
    st.markdown("<h2 style='text-align:center'>🔐 K技術分析平台 登入</h2>", unsafe_allow_html=True)
    username = st.text_input("帳號", "")
    password = st.text_input("密碼（任意填）", type="password")
    if st.button("登入"):
        if username.strip():
            st.session_state.logged_in = True
            st.session_state.username = username.strip()
            st.experimental_rerun()
        else:
            st.error("請輸入帳號")
            st.stop()
    st.stop()  # 直接結束，不往下執行

# ---------- 主畫面 Header ----------
st.image(LOGO_URL, width=80)
st.markdown(f"<div style='text-align:right'>已登入：<span style='color:lightgreen'>{st.session_state.username}</span></div>", unsafe_allow_html=True)
st.title("📈 K 技術分析平台")
st.caption("這是一個整合技術指標、回測模組、股票數據分析的平台。")

# ---------- 使用者輸入區 ----------
ticker = st.text_input("📊 股票代碼 (例如：2330.TW 或 AAPL)", "TSLA")
period_years = st.slider("🧭 回測年限 (年)", 1, 3, 1)
end = datetime.datetime.now()
start = end - datetime.timedelta(days=365 * period_years)

data = yf.download(ticker, start=start, end=end)
if data is None or data.empty:
    st.warning("查無資料，請確認股票代碼是否正確。")
    st.stop()

# ---------- 技術指標選擇 ----------
st.subheader("📌 選擇技術指標")
indicators = st.multiselect(
    "選擇技術指標",
    ["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"]
)

# ---------- 動態參數設定 ----------
if "均線" in indicators:
    st.markdown("### 均線 SMA")
    sma_short = st.number_input("SMA 短期 window", 2, 100, 10)
    sma_long  = st.number_input("SMA 長期 window", 5, 200, 50)
    sma_cross = st.checkbox("顯示 SMA 金叉/死叉點", value=True)
if "MACD" in indicators:
    st.markdown("### MACD")
    macd_fast   = st.number_input("MACD 快線 span", 1, 50, 12)
    macd_slow   = st.number_input("MACD 慢線 span", 1, 50, 26)
    macd_signal = st.number_input("MACD 信號線 span", 1, 20, 9)
if "KDJ" in indicators:
    st.markdown("### KDJ")
    kdj_n = st.number_input("KDJ 計算期間", 2, 50, 14)
    kdj_k = st.number_input("KDJ K 平滑", 1, 20, 3)
    kdj_d = st.number_input("KDJ D 平滑", 1, 20, 3)
if "布林通道" in indicators:
    st.markdown("### 布林通道")
    boll_period = st.number_input("布林通道期間 (Period)", 5, 60, 20)
    boll_k      = st.number_input("布林通道寬度 k (倍數)", 1.0, 3.0, 2.0)

# ---------- 指標計算函數 ----------
def calculate_sma(df, short, long):
    s = df['Close'].rolling(short).mean()
    l = df['Close'].rolling(long).mean()
    cross = (s > l) & (s.shift(1) <= l.shift(1))
    death = (s < l) & (s.shift(1) >= l.shift(1))
    return cross, death

def calculate_macd(df, fast, slow, sig):
    e1 = df['Close'].ewm(span=fast, adjust=False).mean()
    e2 = df['Close'].ewm(span=slow, adjust=False).mean()
    macd = e1 - e2
    sigl = macd.ewm(span=sig, adjust=False).mean()
    cross = (macd > sigl) & (macd.shift(1) <= sigl.shift(1))
    death = (macd < sigl) & (macd.shift(1) >= sigl.shift(1))
    return cross, death

def calculate_kdj(df, n, k_smooth, d_smooth):
    low_min = df['Low'].rolling(n).min()
    high_max = df['High'].rolling(n).max()
    rsv = 100 * (df['Close'] - low_min) / (high_max - low_min)
    k = rsv.ewm(com=k_smooth).mean()
    d = k.ewm(com=d_smooth).mean()
    cross = (k > d) & (k.shift(1) <= d.shift(1))
    death = (k < d) & (k.shift(1) >= d.shift(1))
    return cross, death

def calculate_bollinger(df, period, k):
    mid   = df['Close'].rolling(period).mean()
    std   = df['Close'].rolling(period).std()
    lower = mid - k * std
    upper = mid + k * std
    cross = df['Close'] < lower
    death = df['Close'] > upper
    return cross, death

def calculate_w_pattern(df):
    close = df['Close'].values
    cross = pd.Series(False, index=df.index)
    if len(close) < 5:
        return cross
    for i in range(2, len(close)-2):
        if close[i-2] > close[i-1] < close[i] > close[i+1] < close[i+2]:
            cross.iloc[i] = True
    return cross

def calculate_m_pattern(df):
    close = df['Close'].values
    cross = pd.Series(False, index=df.index)
    if len(close) < 5:
        return cross
    for i in range(2, len(close)-2):
        if close[i-2] < close[i-1] > close[i] < close[i+1] > close[i+2]:
            cross.iloc[i] = True
    return cross

# ---------- 執行分析 ----------
if st.button("🚀 執行分析"):
    results = {}
    markers = {}

    if "均線" in indicators:
        c, d = calculate_sma(data, sma_short, sma_long)
        results['SMA 金叉'] = c
        results['SMA 死叉'] = d
        markers['SMA 金叉'] = ('o', 'red')
        markers['SMA 死叉'] = ('x', 'black')
    if "MACD" in indicators:
        c, d = calculate_macd(data, macd_fast, macd_slow, macd_signal)
        results['MACD 金叉'] = c
        results['MACD 死叉'] = d
        markers['MACD 金叉'] = ('^', 'purple')
        markers['MACD 死叉'] = ('v', 'green')
    if "KDJ" in indicators:
        c, d = calculate_kdj(data, kdj_n, kdj_k, kdj_d)
        results['KDJ 金叉'] = c
        results['KDJ 死叉'] = d
        markers['KDJ 金叉'] = ('^', 'blue')
        markers['KDJ 死叉'] = ('s', 'orange')
    if "布林通道" in indicators:
        c, d = calculate_bollinger(data, boll_period, boll_k)
        results['布林通道跌破下軌'] = c
        results['布林通道突破上軌'] = d
        markers['布林通道跌破下軌'] = ('D', 'magenta')
        markers['布林通道突破上軌'] = ('D', 'cyan')
    if "W底" in indicators:
        c = calculate_w_pattern(data)
        results['W底'] = c
        markers['W底'] = ('*', 'blue')
    if "M頭" in indicators:
        c = calculate_m_pattern(data)
        results['M頭'] = c
        markers['M頭'] = ('*', 'black')

    # 各指標獨立圖表
    for name, series in results.items():
        st.markdown(f"### 📈 {name} 進出場圖")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(data.index, data['Close'], label="收盤價")
        # 修正 ambiguous error 判斷
        if series is not None and not series.empty and series.sum() > 0:
            pts = series[series].index
            m, col = markers[name]
            ax.scatter(pts, data.loc[pts, 'Close'], marker=m, color=col, label=name, s=80)
        ax.set_xlabel("日期")
        ax.set_ylabel("價格")
        ax.legend()
        st.pyplot(fig)

    # 勝率顯示
    st.subheader("📊 各指標勝率")
    for name, series in results.items():
        if series is not None and not series.empty:
            rate = round(series.mean() * 100, 2)
            st.write(f"• {name} 勝率：{rate}%")

    # 複合指標
    if len(results) > 1:
        combined = pd.DataFrame(results).all(axis=1)
        rate = round(combined.mean() * 100, 2)
        st.write(f"• ✅ 複合指標勝率：{rate}%")
        st.markdown("### 📈 複合指標進出場圖")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(data.index, data['Close'], label="收盤價")
        if combined is not None and not combined.empty and combined.sum() > 0:
            pts = combined[combined].index
            ax.scatter(pts, data.loc[pts, 'Close'], marker='*', color='gold', label="複合指標", s=100)
        ax.set_xlabel("日期")
        ax.set_ylabel("價格")
        ax.legend()
        st.pyplot(fig)
