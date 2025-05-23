# 主程式 main.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime

# ---------- LOGO 顯示 ----------

LOGO\_URL = "[https://raw.githubusercontent.com/ken168168ken/my-flask-server/main/logo.png](https://raw.githubusercontent.com/ken168168ken/my-flask-server/main/logo.png)"

# ---------- 登入狀態初始化 ----------

if "logged\_in" not in st.session\_state:
st.session\_state.logged\_in = False

# ---------- 登入頁面 ----------

if not st.session\_state.logged\_in:
st.image(LOGO\_URL, width=80)
st.markdown("## 🔐 K 技術分析平台 登入")
username = st.text\_input("帳號", value="")
password = st.text\_input("密碼（任意填）", type="password")
if st.button("登入"):
if username.strip():
st.session\_state.logged\_in = True
st.session\_state.username = username.strip()
st.experimental\_rerun()
else:
st.error("請輸入帳號")
st.stop()

# ---------- 主畫面 Header ----------

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
sma\_short = st.number\_input("SMA 短期 window", 2, 100, 10)
sma\_long = st.number\_input("SMA 長期 window", 5, 200, 50)
sma\_cross = st.checkbox("顯示 SMA 金叉/死叉點")

st.markdown("### MACD")
macd\_fast = st.number\_input("MACD 快線 span", 1, 50, 12)
macd\_slow = st.number\_input("MACD 慢線 span", 1, 50, 26)
macd\_signal = st.number\_input("MACD 信號線 span", 1, 20, 9)

st.markdown("### KDJ")
kdj\_n = st.number\_input("KDJ 計算期間", 2, 50, 14)
kdj\_k = st.number\_input("KDJ K 平滑", 1, 20, 3)
kdj\_d = st.number\_input("KDJ D 平滑", 1, 20, 3)

st.markdown("### 布林通道")
boll\_period = st.number\_input("布林通道期間 (Period)", 5, 60, 20)
boll\_k = st.number\_input("布林通道寬度 k (倍數)", 1.0, 3.0, 2.0)

# ---------- 指標計算函數 ----------

def calculate\_sma(df, short, long):
s = df\['Close'].rolling(window=short).mean()
l = df\['Close'].rolling(window=long).mean()
cross = (s > l) & (s.shift(1) <= l.shift(1))
death = (s < l) & (s.shift(1) >= l.shift(1))
return cross, death

def calculate\_macd(df, fast, slow, sig):
ema\_fast = df\['Close'].ewm(span=fast, adjust=False).mean()
ema\_slow = df\['Close'].ewm(span=slow, adjust=False).mean()
macd = ema\_fast - ema\_slow
macd\_sig = macd.ewm(span=sig, adjust=False).mean()
cross = (macd > macd\_sig) & (macd.shift(1) <= macd\_sig.shift(1))
death = (macd < macd\_sig) & (macd.shift(1) >= macd\_sig.shift(1))
return cross, death

def calculate\_kdj(df, n, k\_smooth, d\_smooth):
low\_min = df\['Low'].rolling(n).min()
high\_max = df\['High'].rolling(n).max()
rsv = 100 \* (df\['Close'] - low\_min) / (high\_max - low\_min)
k = rsv.ewm(com=k\_smooth).mean()
d = k.ewm(com=d\_smooth).mean()
cross = (k > d) & (k.shift(1) <= d.shift(1))
death = (k < d) & (k.shift(1) >= d.shift(1))
return cross, death

def calculate\_bollinger(df, period, k):
mid = df\['Close'].rolling(window=period).mean()
std = df\['Close'].rolling(window=period).std()
lower = mid - k \* std
upper = mid + k \* std
cross = df\['Close'] < lower
death = df\['Close'] > upper
return cross, death

def calculate\_w\_pattern(df):
cross = pd.Series(False, index=df.index)
for i in range(2, len(df)-2):
if df\['Close']\[i-2] > df\['Close']\[i-1] < df\['Close']\[i] > df\['Close']\[i+1] < df\['Close']\[i+2]:
cross.iloc\[i] = True
return cross

def calculate\_m\_pattern(df):
cross = pd.Series(False, index=df.index)
for i in range(2, len(df)-2):
if df\['Close']\[i-2] < df\['Close']\[i-1] > df\['Close']\[i] < df\['Close']\[i+1] > df\['Close']\[i+2]:
cross.iloc\[i] = True
return cross

# ---------- 執行分析 ----------

if st.button("🚀 執行分析"):
results = {}
markers = {}

```
if "均線" in indicators:
    cross, death = calculate_sma(data, sma_short, sma_long)
    results['SMA Cross'] = cross
    results['SMA Death'] = death
    markers['SMA Cross'] = ('o', 'red')
    markers['SMA Death'] = ('x', 'black')

if "MACD" in indicators:
    cross, death = calculate_macd(data, macd_fast, macd_slow, macd_signal)
    results['MACD Cross'] = cross
    results['MACD Death'] = death
    markers['MACD Cross'] = ('v', 'purple')
    markers['MACD Death'] = ('^', 'green')

if "KDJ" in indicators:
    cross, death = calculate_kdj(data, kdj_n, kdj_k, kdj_d)
    results['KDJ Cross'] = cross
    results['KDJ Death'] = death
    markers['KDJ Cross'] = ('^', 'blue')
    markers['KDJ Death'] = ('s', 'orange')

if "布林通道" in indicators:
    cross, death = calculate_bollinger(data, boll_period, boll_k)
    results['Bollinger Lower'] = cross
    results['Bollinger Upper'] = death
    markers['Bollinger Lower'] = ('D', 'magenta')
    markers['Bollinger Upper'] = ('D', 'cyan')

if "W底" in indicators:
    cross = calculate_w_pattern(data)
    results['W-Bottom'] = cross
    markers['W-Bottom'] = ('*', 'blue')

if "M頭" in indicators:
    cross = calculate_m_pattern(data)
    results['M-Head'] = cross
    markers['M-Head'] = ('*', 'black')

# 單指標圖表
for name, series in results.items():
    st.markdown(f"### 📈 {name} 進出場圖")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data.index, data['Close'], label="Close Price", linewidth=1)
    if series.any():
        pts = series[series].index
        m, c = markers[name]
        ax.scatter(pts, data.loc[pts, 'Close'], marker=m, c=c, label=name, s=80)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")
    st.pyplot(fig)

# 勝率顯示
st.subheader("📊 各指標勝率")
for name, series in results.items():
    rate = round(series.mean() * 100, 2)
    st.write(f"• {name} 勝率：{rate}%")

# 複合指標
if len(results) > 1:
    combined = pd.DataFrame(results).all(axis=1)
    rate = round(combined.mean() * 100, 2)
    st.write(f"• ✅ 複合指標勝率：{rate}%")
    st.markdown("### 📈 複合指標進出場圖")
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
