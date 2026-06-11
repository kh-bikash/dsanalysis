import requests
import pandas as pd
from datetime import datetime

def fetch_btc():
    print("Fetching BTC-USD historical data from Yahoo Finance...")
    # period1: 2023-01-01 (1672531200)
    # period2: 2025-06-01 (1748736000)
    url = "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD?period1=1672531200&period2=1748736000&interval=1d"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        close_prices = result['indicators']['quote'][0]['close']
        open_prices = result['indicators']['quote'][0]['open']
        high_prices = result['indicators']['quote'][0]['high']
        low_prices = result['indicators']['quote'][0]['low']
        
        dates = [datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d') for ts in timestamps]
        
        df = pd.DataFrame({
            'date': dates,
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices
        })
        
        # Drop rows with missing Close prices
        df = df.dropna(subset=['Close'])
        
        print("Successfully fetched BTC-USD data.")
        print("Shape:", df.shape)
        print("Date range:", df['date'].min(), "to", df['date'].max())
        print(df.head(5))
        
        df.to_csv('btc_historical_prices.csv', index=False)
        print("Saved to btc_historical_prices.csv")
        return True
    except Exception as e:
        print("Error fetching from Yahoo Finance:", e)
        return False

if __name__ == '__main__':
    fetch_btc()
