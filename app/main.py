import streamlit as st

st.set_page_config(page_title="K 技術分析平台", layout="wide")
st.markdown("## 📊 K 技術分析平台")
st.markdown("這是一個整合技術指標、回測模組、自選股管理的分析平台。")

st.divider()

col1, col2 = st.columns([1, 2])
with col1:
    st.markdown("### ☑️ 查詢條件")
    st.text_input("輸入股票代碼", placeholder="如：2330.TW 或 AAPL")
    st.multiselect("選擇技術指標", ["均線", "MACD", "KDJ", "布林通道", "W底", "M頭"])
    st.slider("回測區間（年）", 1, 3, 1)
    st.button("執行分析")

with col2:
    st.markdown("### 📈 查詢結果圖表")
    st.info("這裡將顯示股價走勢與技術指標圖。")

st.divider()
st.markdown("🔐 已登入帳號：`ken168168ken`（主帳號） | 模式：`PRO`")
