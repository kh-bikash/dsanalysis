import pandas as pd
import numpy as np

def run_backtest():
    # Load daily BTC prices and Fear & Greed Index
    btc_df = pd.read_csv('btc_historical_prices.csv')
    fgi_df = pd.read_csv('fear_greed_index.csv')
    
    btc_df['date'] = pd.to_datetime(btc_df['date'])
    fgi_df['date'] = pd.to_datetime(fgi_df['date'])
    
    # Merge on date
    df = pd.merge(btc_df, fgi_df[['date', 'value', 'classification']], on='date', how='inner')
    df = df.sort_values(by='date').reset_index(drop=True)
    
    # Filter for the active period of historical data (e.g. Dec 4, 2023 to May 1, 2025)
    # We can also backtest on the full period (Jan 2023 to May 2025) which gives more data.
    # Let's run it on the historical data period (2023-12-04 to 2025-05-01) for consistency with the trader data.
    start_date = '2023-12-04'
    end_date = '2025-05-01'
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)].reset_index(drop=True)
    
    # Calculate daily returns of BTC
    df['BTC_Return'] = df['Close'].pct_change()
    df['BTC_Return'] = df['BTC_Return'].fillna(0)
    
    # We will test different FGI thresholds for the Contrarian Strategy
    # Thresholds: Buy when FGI <= BUY_THRES, Sell when FGI >= SELL_THRES
    BUY_THRES = 30  # Extreme Fear / Fear boundary
    SELL_THRES = 70 # Greed / Extreme Greed boundary
    
    # Simulate Positions
    # 1: Long, 0: Cash, -1: Short (for Long-Short version)
    
    # Long-Only Contrarian
    df['Pos_Contrarian_LongOnly'] = 0
    current_pos = 0
    for i in range(len(df)):
        fgi = df.loc[i, 'value']
        if fgi <= BUY_THRES:
            current_pos = 1  # Buy
        elif fgi >= SELL_THRES:
            current_pos = 0  # Sell / Cash
        df.loc[i, 'Pos_Contrarian_LongOnly'] = current_pos
        
    # Long-Short Contrarian
    df['Pos_Contrarian_LS'] = 0
    current_pos = 0
    for i in range(len(df)):
        fgi = df.loc[i, 'value']
        if fgi <= BUY_THRES:
            current_pos = 1   # Buy / Long
        elif fgi >= SELL_THRES:
            current_pos = -1  # Sell / Short
        df.loc[i, 'Pos_Contrarian_LS'] = current_pos
        
    # Momentum (FOMO) Strategy: Buy Greed, Sell Fear
    df['Pos_Momentum'] = 0
    current_pos = 0
    for i in range(len(df)):
        fgi = df.loc[i, 'value']
        if fgi >= SELL_THRES:
            current_pos = 1   # Buy Greed (FOMO)
        elif fgi <= BUY_THRES:
            current_pos = 0   # Panic Sell
        df.loc[i, 'Pos_Momentum'] = current_pos
        
    # Shift positions by 1 day to avoid look-ahead bias (we trade on today's FGI to get tomorrow's return)
    df['Pos_Contrarian_LongOnly_Shift'] = df['Pos_Contrarian_LongOnly'].shift(1).fillna(0)
    df['Pos_Contrarian_LS_Shift'] = df['Pos_Contrarian_LS'].shift(1).fillna(0)
    df['Pos_Momentum_Shift'] = df['Pos_Momentum'].shift(1).fillna(0)
    
    # Calculate Strategy Returns
    df['Ret_BuyHold'] = df['BTC_Return']
    df['Ret_Contrarian_LongOnly'] = df['Pos_Contrarian_LongOnly_Shift'] * df['BTC_Return']
    df['Ret_Contrarian_LS'] = df['Pos_Contrarian_LS_Shift'] * df['BTC_Return']
    df['Ret_Momentum'] = df['Pos_Momentum_Shift'] * df['BTC_Return']
    
    # Transaction cost simulation (e.g. 0.05% per trade)
    TC = 0.0005
    
    # Calculate transaction fee deductions
    df['Trade_Contrarian_LongOnly'] = df['Pos_Contrarian_LongOnly'].diff().abs().fillna(0)
    df['Trade_Contrarian_LS'] = df['Pos_Contrarian_LS'].diff().abs().fillna(0)
    df['Trade_Momentum'] = df['Pos_Momentum'].diff().abs().fillna(0)
    
    # Deduct transaction costs from return on trade execution days
    df['Ret_Contrarian_LongOnly_Net'] = df['Ret_Contrarian_LongOnly'] - (df['Trade_Contrarian_LongOnly'].shift(1).fillna(0) * TC)
    df['Ret_Contrarian_LS_Net'] = df['Ret_Contrarian_LS'] - (df['Trade_Contrarian_LS'].shift(1).fillna(0) * TC)
    df['Ret_Momentum_Net'] = df['Ret_Momentum'] - (df['Trade_Momentum'].shift(1).fillna(0) * TC)
    
    # Cumulative Returns
    df['Cum_BuyHold'] = (1 + df['Ret_BuyHold']).cumprod()
    df['Cum_Contrarian_LongOnly'] = (1 + df['Ret_Contrarian_LongOnly_Net']).cumprod()
    df['Cum_Contrarian_LS'] = (1 + df['Ret_Contrarian_LS_Net']).cumprod()
    df['Cum_Momentum'] = (1 + df['Ret_Momentum_Net']).cumprod()
    
    # Metrics calculation function
    def compute_metrics(cum_returns, daily_returns, name):
        total_ret = cum_returns.iloc[-1] - 1
        # Annualized return (assuming 365 trading days per year for crypto)
        n_days = len(daily_returns)
        ann_ret = (total_ret + 1) ** (365.0 / n_days) - 1
        
        # Sharpe Ratio (risk-free rate = 0%)
        std = daily_returns.std() * np.sqrt(365)
        sharpe = (ann_ret) / std if std > 0 else np.nan
        
        # Max Drawdown
        running_max = cum_returns.cummax()
        drawdowns = (cum_returns - running_max) / running_max
        max_dd = drawdowns.min()
        
        return {
            'Strategy': name,
            'Total Return': f"{total_ret * 100:.2f}%",
            'Annualized Return': f"{ann_ret * 100:.2f}%",
            'Annualized Volatility': f"{std * 100:.2f}%",
            'Sharpe Ratio': f"{sharpe:.2f}",
            'Max Drawdown': f"{max_dd * 100:.2f}%"
        }
        
    metrics = [
        compute_metrics(df['Cum_BuyHold'], df['Ret_BuyHold'], 'Buy & Hold BTC'),
        compute_metrics(df['Cum_Contrarian_LongOnly'], df['Ret_Contrarian_LongOnly_Net'], 'Contrarian Long-Only (Buy Fear, Sell Greed)'),
        compute_metrics(df['Cum_Contrarian_LS'], df['Ret_Contrarian_LS_Net'], 'Contrarian Long-Short (Buy Fear, Short Greed)'),
        compute_metrics(df['Cum_Momentum'], df['Ret_Momentum_Net'], 'Momentum (Buy Greed, Sell Fear)')
    ]
    
    metrics_df = pd.DataFrame(metrics)
    print("--- Backtest Performance Summary (Period: Dec 4, 2023 to May 1, 2025) ---")
    print(metrics_df.to_string(index=False))
    
    df.to_csv('backtest_results.csv', index=False)
    print("\nSaved backtest results to backtest_results.csv")

if __name__ == '__main__':
    run_backtest()
