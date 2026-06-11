import pandas as pd
import numpy as np

def detailed_behavior():
    df = pd.read_csv('merged_data.csv')
    profiles = pd.read_csv('trader_profiles.csv')
    df = pd.merge(df, profiles[['Account', 'Profitability_Class']], on='Account', how='left')
    
    sentiment_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
    
    # Win rate calculation helper
    def get_win_rate(group):
        pnl_trades = group[group['Closed PnL'] != 0]
        if len(pnl_trades) == 0:
            return np.nan
        return (pnl_trades['Closed PnL'] > 0).sum() / len(pnl_trades)
        
    print("--- Detailed Behavior of Profitable vs Unprofitable Traders ---")
    
    results = []
    for (prof, sent), group in df.groupby(['Profitability_Class', 'classification']):
        win_rate = get_win_rate(group)
        avg_size = group['Size USD'].mean()
        avg_pnl = group['Closed PnL'].mean()
        total_pnl = group['Closed PnL'].sum()
        total_volume = group['Size USD'].sum()
        taker_ratio = group['Crossed'].mean()
        buy_ratio = (group['Side'] == 'BUY').mean()
        
        results.append({
            'Profitability': prof,
            'Sentiment': sent,
            'Win_Rate': win_rate,
            'Avg_Size_USD': avg_size,
            'Avg_PnL_USD': avg_pnl,
            'Total_PnL_USD': total_pnl,
            'Total_Volume_USD': total_volume,
            'Taker_Ratio': taker_ratio,
            'Buy_Ratio': buy_ratio
        })
        
    results_df = pd.DataFrame(results)
    
    # Sort logically
    results_df['Sentiment'] = pd.Categorical(results_df['Sentiment'], categories=sentiment_order, ordered=True)
    results_df = results_df.sort_values(by=['Profitability', 'Sentiment'])
    
    print(results_df.to_string(index=False))
    results_df.to_csv('detailed_sentiment_behavior.csv', index=False)

if __name__ == '__main__':
    detailed_behavior()
