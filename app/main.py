    # 英文名称对照
    eng_map = {
        "均線": "SMA",
        "MACD": "MACD",
        "KDJ": "KDJ",
        "M頭": "M-Head",
        "W底": "W-Bottom",
        "布林通道": "Bollinger Bands",
        "合成": "Combined"
    }

    # Price & Entry Signals
    st.subheader("📈 Price & Entry Signals")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df.index, df["Close"], label="Close Price", color="blue")

    # Marker 样式： (marker, color)
    markers = {
        "均線":        ("o",   "orange"),
        "MACD":       ("^",   "green"),
        "KDJ":        ("s",   "red"),
        "M頭":        ("v",   "purple"),
        "W底":        ("P",   "brown"),
        "布林通道":    ("*",   "pink"),
        "合成":        ("X",   "black"),
    }

    # 先画空的 scatter 以便 legend，只用英文 label
    for ind in signals:
        mk, col = markers[ind]
        ax.scatter([], [], marker=mk, color=col, label=eng_map[ind])

    # 真正绘制进场点
    for ind, ser in signals.items():
        pts = ser[ser].index
        mk, col = markers[ind]
        ax.scatter(pts, df.loc[pts, "Close"],
                   marker=mk, color=col, s=80)

    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left")

    # 在 Streamlit 中显示
    st.pyplot(fig, use_container_width=True)
