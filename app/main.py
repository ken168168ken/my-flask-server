# main.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime

# ---------- LOGO 顯示 ----------

LOGO_URL = "https://github.com/ken168168ken/my-flask-server/raw/main/logo.png"

# ---------- 登入功能 ----------

if "logged\_in" not in st.session\_state:
st.session\_state.logged\_in = False

if not st.session\_state.logged\_in:
st.image(LOGO\_URL, width=80)
st.markdown("""
\## 🔐 K 技術分析平台 登入
""")
username = st.text\_input("帳號", value="")
password = st.text\_input("密碼（任意填）", type="password")
if st.button("登入"):
if username:
st.session\_state.logged\_in = True
st.session\_state.username = username
st.rerun()
else:
st.error("請輸入帳號")
st.stop()

# ---------- 已登入主畫面 ----------

st.image(LOGO\_URL, width=60)
st.markdown(f"已登入：`{st.session_state.username}`")
st.title("📈 K 技術分析平台")
st.caption("這是一個整合技術指標、回測模組、股票數據分析的平台。")

# ---------- 使用者輸入區 ----------

ticker = st.text\_input("📊 股票代碼 (例如：2330.TW 或 AAPL)", value="TSLA")
period\_years = st.slider("🧭 回測年限 (年)", 1, 3, 1)
end = datetime.datetime.now()
start = end - datetime.timedelta(days=365 \* period\_years)
data = yf.download(ticker, start=start, end=end)

# ---------- 技術指標選擇 ----------

st.subheader("📌 選擇技術指標")
indicators = st.multiselect(
"選擇技術指標",
\["均線", "MACD", "KDJ", "M頭", "W底", "布林通道"]
)

# ---------- 參數設定 ----------

st.markdown("### 均線 SMA")
sma\_short = st.number\_input("SMA 短期 window", min\_value=2, max\_value=100, value=10)
sma\_long = st.number\_input("SMA 長期 window", min\_value=5, max\_value=200, value=50)
sma\_cross = st.checkbox("顯示 SMA 金叉死叉點")

st.markdown("### MACD")
macd\_fast = st.number\_input("MACD 快線 span", 1, 50, 12)
macd\_slow = st.number\_input("MACD 慢線 span", 1, 50, 26)
macd\_signal = st.number\_input("MACD 信號線 span", 1, 20, 9)

st.markdown("### KDJ")
kdj\_n = st.number\_input("KDJ 計算期間", 2, 50, 14)
kdj\_k = st.number\_input("KDJ K平滑", 1, 20, 3)
kdj\_d = st.number\_input("KDJ D平滑", 1, 20, 3)

st.markdown("### 布林通道")
boll\_period = st.number\_input("布林通道期間 (Period)", 5, 60, 20)
boll\_k = st.number\_input("布林通道寬度 k (倍數)", 1.0, 3.0, 2.0)

# ---------- 技術指標函數 ----------

def calculate\_sma(df, short, long):
sma\_s = df\['Close'].rolling(window=short).mean()
sma\_l = df\['Close'].rolling(window=long).mean()
signal = (sma\_s > sma\_l) & (sma\_s.shift(1) <= sma\_l.shift(1))
return signal

def calculate\_macd(df, fast, slow, signal):
ema\_fast = df\['Close'].ewm(span=fast, adjust=False).mean()
ema\_slow = df\['Close'].ewm(span=slow, adjust=False).mean()
macd = ema\_fast - ema\_slow
macd\_signal = macd.ewm(span=signal, adjust=False).mean()
signal = (macd > macd\_signal) & (macd.shift(1) <= macd\_signal.shift(1))
return signal

def calculate\_kdj(df, n, k\_smooth, d\_smooth):
low\_min = df\['Low'].rolling(n).min()
high\_max = df\['High'].rolling(n).max()
rsv = 100 \* (df\['Close'] - low\_min) / (high\_max - low\_min)
k = rsv.ewm(com=k\_smooth).mean()
d = k.ewm(com=d\_smooth).mean()
signal = (k > d) & (k.shift(1) <= d.shift(1))
return signal

def calculate\_bollinger(df, period, k):
mid = df\['Close'].rolling(window=period).mean()
std = df\['Close'].rolling(window=period).std()
upper = mid + k \* std
lower = mid - k \* std
signal = (df\['Close'] < lower) | (df\['Close'] > upper)
return signal

def calculate\_w\_pattern(df):
signal = pd.Series(False, index=df.index)
for i in range(2, len(df) - 2):
if df\['Close']\[i-2] > df\['Close']\[i-1] < df\['Close']\[i] > df\['Close']\[i+1] < df\['Close']\[i+2]:
signal.iloc\[i] = True
return signal

def calculate\_m\_pattern(df):
signal = pd.Series(False, index=df.index)
for i in range(2, len(df) - 2):
if df\['Close']\[i-2] < df\['Close']\[i-1] > df\['Close']\[i] < df\['Close']\[i+1] > df\['Close']\[i+2]:
signal.iloc\[i] = True
return signal

# ---------- 執行分析 ----------

if st.button("🚀 執行分析"):
signals = {}
markers = {}

```
if "均線" in indicators:
    signal = calculate_sma(data, sma_short, sma_long)
    signals['SMA'] = signal
    markers['SMA'] = ('o', 'red')

if "MACD" in indicators:
    signal = calculate_macd(data, macd_fast, macd_slow, macd_signal)
    signals['MACD'] = signal
    markers['MACD'] = ('v', 'purple')

if "KDJ" in indicators:
    signal = calculate_kdj(data, kdj_n, kdj_k, kdj_d)
    signals['KDJ'] = signal
    markers['KDJ'] = ('^', 'green')

if "布林通道" in indicators:
    signal = calculate_bollinger(data, boll_period, boll_k)
    signals['Bollinger Bands'] = signal
    markers['Bollinger Bands'] = ('s', 'magenta')

if "W底" in indicators:
    signal = calculate_w_pattern(data)
    signals['W-Bottom'] = signal
    markers['W-Bottom'] = ('D', 'blue')

if "M頭" in indicators:
    signal = calculate_m_pattern(data)
    signals['M-Head'] = signal
    markers['M-Head'] = ('X', 'black')

for name, signal in signals.items():
    st.markdown(f"### 📈 價格與{name} 進出場圖")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data.index, data['Close'], label="Close Price", linewidth=1)
    if signal.any():
        pts = signal[signal].index
        m, c = markers[name]
        ax.scatter(pts, data.loc[pts, 'Close'], marker=m, color=c, label=name, s=80)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    st.pyplot(fig)

st.subheader("📊 各指標勝率")
for name, signal in signals.items():
    rate = round(signal.mean() * 100, 2)
    st.write(f"• {name} 勝率：{rate}%")

if len(signals) >= 2:
    combined = pd.DataFrame(signals).all(axis=1)
    rate = round(combined.mean() * 100, 2)
    st.write(f"• ✅ 複合指標勝率：{rate}%")
    st.markdown("### 📈 價格與複合指標進出場圖")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data.index, data['Close'], label="Close Price", linewidth=1)
    if combined.any():
        pts = combined[combined].index
        ax.scatter(pts, data.loc[pts, 'Close'], marker='*', color='gold', label="Combined", s=100)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    st.pyplot(fig)
```
