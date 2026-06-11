import pandas as pd
import numpy as np

def profile_traders():
    df = pd.read_csv('merged_data.csv')
    
    # Group by trader account
    profiles = []
    
    for account, group in df.groupby('Account'):
        total_pnl = group['Closed PnL'].sum()
        total_fee = group['Fee'].sum()
        net_pnl = total_pnl - total_fee
        total_volume = group['Size USD'].sum()
        trade_count = len(group)
        
        # Calculate win rate
        pnl_trades = group[group['Closed PnL'] != 0]
        pnl_trade_count = len(pnl_trades)
        wins = (pnl_trades['Closed PnL'] > 0).sum()
        win_rate = wins / pnl_trade_count if pnl_trade_count > 0 else np.nan
        
        avg_trade_size = group['Size USD'].mean()
        avg_fee = group['Fee'].mean()
        
        # Taker trade ratio
        taker_ratio = group['Crossed'].mean()
        
        # Favorite coin
        favorite_coin = group['Coin'].mode().iloc[0] if not group['Coin'].empty else 'N/A'
        
        profiles.append({
            'Account': account,
            'Total_PnL': total_pnl,
            'Total_Fee': total_fee,
            'Net_PnL': net_pnl,
            'Total_Volume': total_volume,
            'Trade_Count': trade_count,
            'PnL_Trade_Count': pnl_trade_count,
            'Win_Rate': win_rate,
            'Avg_Trade_Size': avg_trade_size,
            'Avg_Fee': avg_fee,
            'Taker_Ratio': taker_ratio,
            'Favorite_Coin': favorite_coin
        })
        
    profiles_df = pd.DataFrame(profiles)
    
    # Sort by Net PnL descending
    profiles_df = profiles_df.sort_values(by='Net_PnL', ascending=False)
    
    # Classifications
    # 1. Profitability: Profitable if Net_PnL > 0, else Unprofitable
    profiles_df['Profitability_Class'] = np.where(profiles_df['Net_PnL'] > 0, 'Profitable', 'Unprofitable')
    
    # 2. Trader Size: Whale if Total_Volume > median, else Retail
    median_vol = profiles_df['Total_Volume'].median()
    profiles_df['Size_Class'] = np.where(profiles_df['Total_Volume'] > median_vol, 'Whale', 'Retail')
    
    # 3. Frequency: High Frequency if Trade_Count > median, else Low Frequency
    median_count = profiles_df['Trade_Count'].median()
    profiles_df['Freq_Class'] = np.where(profiles_df['Trade_Count'] > median_count, 'High Frequency', 'Low Frequency')
    
    print("Trader Profiles (sorted by Net PnL):")
    print(profiles_df[['Account', 'Net_PnL', 'Total_Volume', 'Trade_Count', 'Win_Rate', 'Profitability_Class', 'Size_Class']].to_string(index=False))
    
    profiles_df.to_csv('trader_profiles.csv', index=False)
    print("\nProfiles saved to trader_profiles.csv.")
    
    # Aggregate stats for profitable vs unprofitable
    print("\nAggregate Stats by Profitability Class:")
    agg_pnl = profiles_df.groupby('Profitability_Class').agg({
        'Account': 'count',
        'Net_PnL': 'mean',
        'Total_Volume': 'mean',
        'Trade_Count': 'mean',
        'Win_Rate': 'mean',
        'Taker_Ratio': 'mean'
    }).rename(columns={'Account': 'Count'})
    print(agg_pnl)

if __name__ == '__main__':
    profile_traders()
