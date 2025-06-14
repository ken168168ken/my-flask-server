import pandas as pd
import numpy as np
from datetime import datetime, time, timezone, timedelta
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify
import schedule
import time
import threading

app = Flask(__name__)

class StockStrategy:
    def __init__(self):
        self.api_key = 'FFKRFB16QBUBTH2D'
        self.subscribed_emails = set()
        # 擴展默認分析標的，包含不同市場類型
        self.default_symbols = {
            'US_SP500': [
                'AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'META', 'BRK-B', 'XOM', 
                'UNH', 'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
                'LLY', 'PFE', 'KO', 'BAC', 'PEP', 'TMO', 'COST', 'AVGO', 'WMT',
                'DIS', 'CSCO', 'ABT', 'MCD', 'ACN', 'DHR', 'NEE', 'VZ', 'TXN'
            ],
            'TW_LISTED': [
                '2330.TW', '2317.TW', '2454.TW', '2412.TW', '2308.TW', '2303.TW',
                '2881.TW', '2882.TW', '2002.TW', '1301.TW', '2891.TW', '3711.TW',
                '2886.TW', '2884.TW', '2885.TW', '2892.TW', '2357.TW', '2382.TW',
                '3045.TW', '2880.TW', '5880.TW', '2883.TW', '2327.TW', '2395.TW',
                '2912.TW', '2301.TW', '1303.TW', '1216.TW', '2207.TW', '2474.TW'
            ],
            'TW_OTC': [
                '6488.TWO', '3105.TWO', '4743.TWO', '3293.TWO', '8299.TWO',
                '4966.TWO', '3227.TWO', '8299.TWO', '6121.TWO', '4123.TWO',
                '3548.TWO', '3252.TWO', '4174.TWO', '3680.TWO', '4147.TWO',
                '3455.TWO', '3218.TWO', '4162.TWO', '3228.TWO', '4736.TWO'
            ],
            'ETFs': [
                'SPY', 'QQQ', 'VTI', '0050.TW', '0056.TW', '00878.TW', 
                '00919.TW', '00929.TW', '00635U.TW', '006208.TW', 'VOO', 
                'IVV', 'VEA', 'IEFA', 'VWO', 'IEMG', 'BND', 'AGG', 'VIG'
            ],
            'COMMODITIES': ['GC=F', 'SI=F', 'CL=F'],  # 黃金、白銀、原油期貨
            'FOREX': ['EURUSD=X', 'USDJPY=X', 'GBPUSD=X', 'AUDUSD=X']
        }

    def calculate_rsi(self, data, periods=14):
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def detect_pin_bar(self, data):
        data['Body'] = abs(data['Close'] - data['Open'])
        data['Upper_Shadow'] = data['High'] - data[['Open', 'Close']].max(axis=1)
        data['Lower_Shadow'] = data[['Open', 'Close']].min(axis=1) - data['Low']
        data['Range'] = data['High'] - data['Low']
        
        body_ratio = data['Body'] / data['Range'] < 0.2
        upper_shadow_ratio = data['Upper_Shadow'] / data['Range'] > 0.6
        lower_shadow_ratio = data['Lower_Shadow'] / data['Range'] > 0.6
        
        bullish_pin = body_ratio & lower_shadow_ratio
        bearish_pin = body_ratio & upper_shadow_ratio
        
        return bullish_pin, bearish_pin

    def detect_double_top_bottom(self, data):
        window = 20
        tolerance = 0.02
        
        data['Local_High'] = data['High'].rolling(window=window, center=True).max()
        data['Local_Low'] = data['Low'].rolling(window=window, center=True).min()
        
        double_tops = []
        double_bottoms = []
        
        for i in range(window, len(data)-window):
            if abs(data['High'].iloc[i] - data['Local_High'].iloc[i]) < tolerance * data['High'].iloc[i]:
                for j in range(i+5, i+window):
                    if abs(data['High'].iloc[j] - data['High'].iloc[i]) < tolerance * data['High'].iloc[i]:
                        if min(data['Low'].iloc[i:j]) < min(data['Low'].iloc[i-5:i]) * 0.98:
                            double_tops.append(i)
                            break
            
            if abs(data['Low'].iloc[i] - data['Local_Low'].iloc[i]) < tolerance * data['Low'].iloc[i]:
                for j in range(i+5, i+window):
                    if abs(data['Low'].iloc[j] - data['Low'].iloc[i]) < tolerance * data['Low'].iloc[i]:
                        if max(data['High'].iloc[i:j]) > max(data['High'].iloc[i-5:i]) * 1.02:
                            double_bottoms.append(i)
                            break
        
        return double_tops, double_bottoms

    def analyze_stock(self, symbol, start_date=None, end_date=None):
        try:
            # 處理時區問題
            if start_date:
                start_date = pd.Timestamp(start_date).tz_localize('Asia/Taipei')
            if end_date:
                end_date = pd.Timestamp(end_date).tz_localize('Asia/Taipei')

            stock = yf.Ticker(symbol)
            data = stock.history(start=start_date, end=end_date)
            
            if len(data) == 0:
                return None
            
            data['RSI'] = self.calculate_rsi(data)
            data['MA50'] = data['Close'].rolling(window=50).mean()
            data['Vol_MA20'] = data['Volume'].rolling(window=20).mean()
            
            bullish_pin, bearish_pin = self.detect_pin_bar(data)
            double_tops, double_bottoms = self.detect_double_top_bottom(data)
            
            signals = []
            for i in range(len(data)):
                if bullish_pin.iloc[i] and data['RSI'].iloc[i] < 30:
                    signals.append({
                        'date': data.index[i].strftime('%Y-%m-%d'),
                        'type': 'Bullish Pin Bar',
                        'price': round(data['Close'].iloc[i], 2),
                        'rsi': round(data['RSI'].iloc[i], 2)
                    })
                elif bearish_pin.iloc[i] and data['RSI'].iloc[i] > 70:
                    signals.append({
                        'date': data.index[i].strftime('%Y-%m-%d'),
                        'type': 'Bearish Pin Bar',
                        'price': round(data['Close'].iloc[i], 2),
                        'rsi': round(data['RSI'].iloc[i], 2)
                    })
                
                if i in double_tops:
                    signals.append({
                        'date': data.index[i].strftime('%Y-%m-%d'),
                        'type': 'Double Top',
                        'price': round(data['Close'].iloc[i], 2),
                        'rsi': round(data['RSI'].iloc[i], 2)
                    })
                elif i in double_bottoms:
                    signals.append({
                        'date': data.index[i].strftime('%Y-%m-%d'),
                        'type': 'Double Bottom',
                        'price': round(data['Close'].iloc[i], 2),
                        'rsi': round(data['RSI'].iloc[i], 2)
                    })
            
            # 添加市場類型標識
            market_type = next((market for market, symbols in self.default_symbols.items() 
                              if symbol in symbols), 'OTHER')
            
            return {'symbol': symbol, 'market_type': market_type, 'signals': signals}
        except Exception as e:
            print(f"Error analyzing stock {symbol}: {str(e)}")
            return None

    def analyze_all_stocks(self, start_date=None, end_date=None):
        all_results = []
        # 遍歷所有市場類型的所有標的
        for market_type, symbols in self.default_symbols.items():
            for symbol in symbols:
                result = self.analyze_stock(symbol, start_date, end_date)
                if result:
                    all_results.append(result)
        return all_results

    def send_email(self, email_address, signals, symbol, market_type):
        if not signals:
            return
        
        msg = MIMEMultipart()
        msg['From'] = 'your_email@gmail.com'  # 需要設置發件人郵箱
        msg['To'] = email_address
        msg['Subject'] = f'Trading Signals - {market_type} - {symbol} - {datetime.now().strftime("%Y-%m-%d")}'
        
        body = f"Trading signals for {symbol} ({market_type}):\n\n"
        for signal in signals:
            body += f"Date: {signal['date']}\n"
            body += f"Type: {signal['type']}\n"
            body += f"Price: {signal['price']}\n"
            body += f"RSI: {signal['rsi']}\n\n"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # 這裡需要設置您的SMTP服務器信息
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('your_email@gmail.com', 'your_password')
        server.send_message(msg)
        server.quit()

    def subscribe_email(self, email):
        self.subscribed_emails.add(email)

    def check_and_send_signals(self):
        for email in self.subscribed_emails:
            results = self.analyze_all_stocks()
            for result in results:
                if result['signals']:
                    self.send_email(email, result['signals'], result['symbol'], result['market_type'])

strategy = StockStrategy()

def schedule_checker():
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    results = strategy.analyze_all_stocks(start_date, end_date)
    return render_template('results.html', results=results)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    strategy.subscribe_email(email)
    return 'Successfully subscribed!'

if __name__ == '__main__':
    # 設置定時任務
    schedule.every().day.at("07:00").do(strategy.check_and_send_signals)
    schedule.every().day.at("15:00").do(strategy.check_and_send_signals)
    
    # 啟動定時任務線程
    scheduler_thread = threading.Thread(target=schedule_checker)
    scheduler_thread.start()
    
    # 啟動Flask應用
    app.run(debug=True)
