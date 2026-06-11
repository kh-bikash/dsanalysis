import pandas as pd
import numpy as np

def analyze_correlation():
    # Load datasets
    df = pd.read_csv('merged_data.csv')
    profiles = pd.read_csv('trader_profiles.csv')
    
    # Map trader classifications back to the merged data
    df = pd.merge(df, profiles[['Account', 'Profitability_Class', 'Size_Class', 'Freq_Class']], on='Account', how='left')
    
    # Define sentiment ordering
    sentiment_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
    
    # 1. Trading Activity by Sentiment
    print("--- 1. Trading Activity by Sentiment (All Traders) ---")
    activity = df.groupby('classification').agg({
        'Size USD': ['sum', 'mean', 'count'],
        'Closed PnL': ['sum', 'mean']
    }).reindex(sentiment_order)
    
    # Rename columns for readability
    activity.columns = ['Total_Volume_USD', 'Avg_Trade_Size_USD', 'Trade_Count', 'Total_Realized_PnL', 'Avg_Realized_PnL']
    print(activity)
    print("\n" + "="*60 + "\n")
    
    # 2. Buy vs Sell Ratio by Sentiment (Herd Behavior)
    # Side is BUY or SELL
    print("--- 2. Buy vs Sell Ratio by Sentiment (Herd Behavior) ---")
    # We will map BUY to +1 and SELL to -1, or compute BUY%
    df['Is_Buy'] = np.where(df['Side'] == 'BUY', 1, 0)
    df['Side_Val'] = np.where(df['Side'] == 'BUY', 1, -1)
    
    buy_ratio = df.groupby('classification').agg({
        'Is_Buy': 'mean',
        'Size USD': 'sum',
        'Side_Val': 'count'
    }).reindex(sentiment_order).rename(columns={'Is_Buy': 'Buy_Ratio', 'Side_Val': 'Trade_Count'})
    print(buy_ratio)
    print("\n" + "="*60 + "\n")
    
    # 3. Profitable vs Unprofitable Traders Behavior
    print("--- 3. Behavior of Profitable vs Unprofitable Traders ---")
    prof_groups = df.groupby(['Profitability_Class', 'classification']).agg({
        'Size USD': 'sum',
        'Is_Buy': 'mean',
        'Closed PnL': ['sum', 'mean']
    }).reindex(pd.MultiIndex.from_product([['Profitable', 'Unprofitable'], sentiment_order], names=['Profitability', 'Sentiment']))
    
    prof_groups.columns = ['Total_Volume_USD', 'Buy_Ratio', 'Total_Realized_PnL', 'Avg_Realized_PnL']
    print(prof_groups)
    print("\n" + "="*60 + "\n")
    
    # 4. Correlation Analysis
    print("--- 4. Correlation Analysis (Fear & Greed Index Value vs. Trade Variables) ---")
    # Let's compute correlation between index value and trade size, closed PnL, and Side_Val
    # Pearson
    corr_pearson = df[['value', 'Size USD', 'Closed PnL', 'Side_Val']].corr(method='pearson')
    print("Pearson Correlation:")
    print(corr_pearson['value'])
    
    # Spearman
    corr_spearman = df[['value', 'Size USD', 'Closed PnL', 'Side_Val']].corr(method='spearman')
    print("\nSpearman Correlation:")
    print(corr_spearman['value'])
    print("\n" + "="*60 + "\n")
    
    # 5. Let's look at the correlation for each trader individually
    print("--- 5. Top 5 Profitable vs Bottom 5 Unprofitable Traders Sentiment-Direction Correlations ---")
    # Does a positive correlation between FGI and Side_Val mean they buy when Greed is high (momentum)?
    # Negative correlation means they buy when FGI is low (contrarian / buying fear)?
    trader_corrs = []
    for account, group in df.groupby('Account'):
        # Only compute if they have enough trades
        if len(group) > 50:
            pearson_corr_side = group['value'].corr(group['Side_Val'], method='pearson')
            pearson_corr_pnl = group['value'].corr(group['Closed PnL'], method='pearson')
            
            # Profitable status
            net_pnl = profiles.loc[profiles['Account'] == account, 'Net_PnL'].values[0]
            prof_class = profiles.loc[profiles['Account'] == account, 'Profitability_Class'].values[0]
            
            trader_corrs.append({
                'Account': account,
                'Net_PnL': net_pnl,
                'Profitability': prof_class,
                'FGI_Side_Corr': pearson_corr_side,
                'FGI_PnL_Corr': pearson_corr_pnl
            })
            
    trader_corrs_df = pd.DataFrame(trader_corrs).sort_values(by='Net_PnL', ascending=False)
    print("Top 10 Profitable Traders Correlations:")
    print(trader_corrs_df.head(10).to_string(index=False))
    print("\nBottom Traders Correlations:")
    print(trader_corrs_df.tail(5).to_string(index=False))
    
    # Average correlations by group
    print("\nAverage FGI-Side Correlation by Profitability Group:")
    print(trader_corrs_df.groupby('Profitability')['FGI_Side_Corr'].mean())

if __name__ == '__main__':
    analyze_correlation()
