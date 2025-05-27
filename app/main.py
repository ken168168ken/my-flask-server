# inertia_rebound/app.py
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/rebound")
def rebound(symbol: str = Query(..., description="股票代碼"), years: int = 5):
    interval_map = {'day':'1d', 'week':'1wk', 'month':'1mo'}
    result = {}
    for period, interval in interval_map.items():
        end = datetime.today()
        start = end - timedelta(days=365*years)
        df = yf.download(symbol, start=start.strftime('%Y-%m-%d'), end=end.strftime('%Y-%m-%d'), interval=interval)
        if df.empty:
            result[period] = {'error': 'No data found'}
            continue
        ma_candidate = [5,10,13,20,30,60,120,240]
        best_ma = None
        best_rate = 0
        rebound_cnt = win_cnt = 0
        for ma in ma_candidate:
            col = f"MA{ma}"
            df[col] = df['Close'].rolling(window=ma).mean()
            rc, wc = 0, 0
            for i in range(ma, len(df)-5):
                if (df['Close'].iloc[i-1] > df[col].iloc[i-1]) and (df['Close'].iloc[i] <= df[col].iloc[i]):
                    rc += 1
                    future_close = df['Close'].iloc[i+1:i+6]
                    base = df['Close'].iloc[i]
                    if (future_close > base*1.03).any():
                        wc += 1
            if rc > 0 and wc/rc > best_rate:
                best_ma = ma
                best_rate = wc/rc
                rebound_cnt = rc
                win_cnt = wc
        result[period] = {
            'best_ma': best_ma,
            'winrate': round(best_rate, 3),
            'rebound_cnt': rebound_cnt,
            'win_cnt': win_cnt
        }
    return JSONResponse(content=result)
