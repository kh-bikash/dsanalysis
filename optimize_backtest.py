import pandas as pd
import numpy as np

def optimize_thresholds():
    btc_df = pd.read_csv('btc_historical_prices.csv')
    fgi_df = pd.read_csv('fear_greed_index.csv')
    
    btc_df['date'] = pd.to_datetime(btc_df['date'])
    fgi_df['date'] = pd.to_datetime(fgi_df['date'])
    
    df = pd.merge(btc_df, fgi_df[['date', 'value']], on='date', how='inner')
    df = df.sort_values(by='date').reset_index(drop=True)
    
    start_date = '2023-12-04'
    end_date = '2025-05-01'
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)].reset_index(drop=True)
    
    df['BTC_Return'] = df['Close'].pct_change().fillna(0)
    
    results = []
    
    # We will test buy thresholds from 20 to 50, and sell thresholds from 50 to 90
    for buy_t in range(20, 51, 5):
        for sell_t in range(50, 91, 5):
            if buy_t >= sell_t:
                continue
                
            # Simulate Long-Only
            pos = 0
            positions = []
            for val in df['value']:
                if val <= buy_t:
                    pos = 1
                elif val >= sell_t:
                    pos = 0
                positions.append(pos)
                
            # Shift
            positions_shift = [0] + positions[:-1]
            
            # Returns
            ret = np.array(positions_shift) * df['BTC_Return'].values
            
            # Cumulative
            cum_ret = np.cumprod(1 + ret)
            total_ret = cum_ret[-1] - 1
            
            # Volatility & Sharpe
            vol = np.std(ret) * np.sqrt(365)
            ann_ret = (total_ret + 1) ** (365.0 / len(df)) - 1
            sharpe = ann_ret / vol if vol > 0 else np.nan
            
            # Drawdown
            running_max = np.maximum.accumulate(cum_ret)
            drawdowns = (cum_ret - running_max) / running_max
            max_dd = np.min(drawdowns)
            
            results.append({
                'Buy_Thres': buy_t,
                'Sell_Thres': sell_t,
                'Total_Return': total_ret,
                'Annualized_Return': ann_ret,
                'Volatility': vol,
                'Sharpe': sharpe,
                'Max_Drawdown': max_dd
            })
            
    res_df = pd.DataFrame(results).sort_values(by='Sharpe', ascending=False)
    print("Top 10 Optimized Parameter Combinations (Sorted by Sharpe Ratio):")
    print(res_df.head(10).to_string(index=False))

if __name__ == '__main__':
    optimize_thresholds()
