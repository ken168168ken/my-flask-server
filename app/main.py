```python
# 主程式 main.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime

# ---------- LOGO 顯示 ----------
LOGO_URL = "https://github.com/ken168168ken/my-flask-server/raw/main/logo.png"

# ---------- 登入功能 ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.image(LOGO_URL, width=80)
    st.markdown("## 🔐 K 技術分析平台 登入")
    username = st.text_input("帳號", value="")
    password = st.text_input("密碼（任意填）", type="password")
    if st.button("登入"):
        if username:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("請輸入帳號")
    st.stop()

# ---------- 已登入主畫面 ----------
st.image(LOGO_URL, width=60)
st.markdown(f"已登入：`{st.session_state.username}`")
st.title("📈 K 技術分析平台")
st.caption("這是一個整合技術指標、回測模組、股票數據分析的平台。")

# ---------- 使用者輸入區 ----------
ticker = st.text_input("📊 股票代碼 (例如：2330.TW 或 AAPL)", value="TSLA")
period_years = st.slider("🧭 回測年限 (年)", 1, 3, 1)
end = datetime.datetime.now()
start = end - datetime.timedelta(days=365 * period_years)
data = yf.download(ticker, start=start, end=end)

# ---------- 技術指標選擇 ----------
st.subheader("📌 選擇技術指標")
indicators = st.multiselect(
    "選擇技術指標",
    ["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"]
)

# ---------- 參數設定 ----------
st.markdown("### 均線 SMA")
sma_short = st.number_input("SMA 短期 window", 2, 100, 10)
sma_long = st.number_input("SMA 長期 window", 5, 200, 50)
sma_cross = st.checkbox("顯示 SMA 金叉死叉點")

st.markdown("### MACD")
macd_fast = st.number_input("MACD 快線 span", 1, 50, 12)
macd_slow = st.number_input("MACD 慢線 span", 1, 50, 26)
macd_signal = st.number_input("MACD 信號線 span", 1, 20, 9)

st.markdown("### KDJ")
kdj_n = st.number_input("KDJ 計算期間", 2, 50, 14)
kdj_k = st.number_input("KDJ K 平滑", 1, 20, 3)
kdj_d = st.number_input("KDJ D 平滑", 1, 20, 3)

st.markdown("### 布林通道")
boll_period = st.number_input("布林通道期間 (Period)", 5, 60, 20)
boll_k = st.number_input("布林通道寬度 k (倍數)", 1.0, 3.0, 2.0)

# ---------- 技術指標函數 ----------
def calculate_sma(df, short, long):
    s = df['Close'].rolling(window=short).mean()
    l = df['Close'].rolling(window=long).mean()
    signal = (s > l) & (s.shift(1) <= l.shift(1))
    return signal


def calculate_macd(df, fast, slow, sig):
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_sig = macd.ewm(span=sig, adjust=False).mean()
    signal = (macd > macd_sig) & (macd.shift(1) <= macd_sig.shift(1))
    return signal


def calculate_kdj(df, n, k_smooth, d_smooth):
    low_min = df['Low'].rolling(n).min()
    high_max = df['High'].rolling(n).max()
    rsv = 100 * (df['Close'] - low_min) / (high_max - low_min)
    k = rsv.ewm(com=k_smooth).mean()
    d = k.ewm(com=d_smooth).mean()
    signal = (k > d) & (k.shift(1) <= d.shift(1))
    return signal


def calculate_bollinger(df, period, k):
    mid = df['Close'].rolling(window=period).mean()
    std = df['Close'].rolling(window=period).std()
    lower = mid - k * std
    upper = mid + k * std
    signal = (df['Close'] < lower) | (df['Close'] > upper)
    return signal


def calculate_w_pattern(df):
    sig = pd.Series(False, index=df.index)
    for i in range(2, len(df)-2):
        if df['Close'][i-2] > df['Close'][i-1] < df['Close'][i] > df['Close'][i+1] < df['Close'][i+2]:
            sig.iloc[i] = True
    return sig


def calculate_m_pattern(df):
    sig = pd.Series(False, index=df.index)
    for i in range(2, len(df)-2):
        if df['Close'][i-2] < df['Close'][i-1] > df['Close'][i] < df['Close'][i+1] > df['Close'][i+2]:
            sig.iloc[i] = True
    return sig

# ---------- 執行分析 ----------
if st.button("🚀 執行分析"):
    signals = {}
    markers = {}

    # 計算並收集信號
    if "均線" in indicators:
        signals['SMA'] = calculate_sma(data, sma_short, sma_long)
        markers['SMA'] = ('o', 'red')
    if "MACD" in indicators:
        signals['MACD'] = calculate_macd(data, macd_fast, macd_slow, macd_signal)
        markers['MACD'] = ('v', 'purple')
    if "KDJ" in indicators:
        signals['KDJ'] = calculate_kdj(data, kdj_n, kdj_k, kdj_d)
        markers['KDJ'] = ('^', 'green')
    if "布林通道" in indicators:
        signals['Bollinger Bands'] = calculate_bollinger(data, boll_period, boll_k)
        markers['Bollinger Bands'] = ('s', 'magenta')
    if "W底" in indicators:
        signals['W-Bottom'] = calculate_w_pattern(data)
        markers['W-Bottom'] = ('D', 'blue')
    if "M頭" in indicators:
        signals['M-Head'] = calculate_m_pattern(data)
        markers['M-Head'] = ('X', 'black')

    # 各指標獨立圖表
    for name, sig in signals.items():
        st.markdown(f"### 📈 價格與{name} 進出場圖")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(data.index, data['Close'], label="Close Price", linewidth=1)
        if sig.any():
            pts = sig[sig].index
            m, c = markers[name]
            ax.scatter(pts, data.loc[pts, 'Close'], marker=m, c=c, label=name, s=80)
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend(loc="upper left")
        st.pyplot(fig)

    # 顯示勝率
    st.subheader("📊 各指標勝率")
    for name, sig in signals.items():
        rate = round(sig.mean()*100, 2)
        st.write(f"• {name} 勝率：{rate}%")

    # 複合指標
    if len(signals) >= 2:
        combined = pd.DataFrame(signals).all(axis=1)
        rate = round(combined.mean()*100, 2)
        st.write(f"• ✅ 複合指標勝率：{rate}%")
        st.markdown("### 📈 價格與複合指標進出場圖")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(data.index, data['Close'], label="Close Price", linewidth=1)
        if combined.any():
            pts = combined[combined].index
            ax.scatter(pts, data.loc[pts, 'Close'], marker='*', c='gold', label="Combined", s=100)
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend(loc="upper left")
        st.pyplot(fig)
```
