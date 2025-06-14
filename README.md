# 股票策略分析系統

這是一個基於Python的股票策略分析系統，能夠識別Pin Bar和Double Top/Bottom形態，並提供即時的交易信號。

## 功能特點

- 支持Pin Bar形態識別
  - Bullish Pin Bar（看漲）
  - Bearish Pin Bar（看跌）
- 支持Double Top/Bottom形態識別
  - Double Top（雙頂）
  - Double Bottom（雙底）
- 技術指標支持
  - RSI（相對強弱指數）
  - MA50（50日移動平均線）
  - Vol_MA20（20日成交量移動平均線）
- 自動郵件提醒服務
  - 每日早上7點和下午3點自動掃描
  - 發送符合條件的交易信號
- 網頁界面
  - 即時查詢分析結果
  - 訂閱郵件提醒服務

## 安裝說明

1. 克隆代碼庫：
```bash
git clone [repository_url]
cd stock_trae
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 配置郵件服務：
在`stock_backtest.py`中修改以下配置：
```python
msg['From'] = 'your_email@gmail.com'  # 修改為您的郵箱
server.login('your_email@gmail.com', 'your_password')  # 修改為您的郵箱和密碼
```

4. 運行應用：
```bash
python stock_backtest.py
```

## 使用說明

1. 訪問網頁界面：
   - 打開瀏覽器訪問 `http://localhost:5000`

2. 股票分析：
   - 輸入股票代碼（例如：AAPL, 2330.TW）
   - 選擇開始和結束日期
   - 點擊「分析」按鈕查看結果

3. 訂閱提醒：
   - 在首頁輸入您的電子郵件地址
   - 點擊「訂閱」按鈕
   - 系統將在每日指定時間發送分析結果

## API密鑰

系統使用Alpha Vantage API獲取股票數據，API密鑰已配置：
```
FFKRFB16QBUBTH2D
```

## 擴展性

系統設計支持添加新的交易策略和技術指標。要添加新的策略，只需：

1. 在`StockStrategy`類中添加新的分析方法
2. 在`analyze_stock`方法中整合新策略
3. 更新網頁模板顯示新的分析結果

## 注意事項

- 請確保您的郵件服務器配置正確
- 建議使用虛擬環境運行應用
- 注意API使用限制和頻率

## 貢獻

歡迎提交Issue和Pull Request來改進這個項目。

## 授權

MIT License
