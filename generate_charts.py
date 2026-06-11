import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Set style for professional premium looks
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#EEEEEE'
plt.rcParams['grid.linewidth'] = 0.5

# Define colors
PRIMARY_COLOR = '#3F51B5' # Indigo
SECONDARY_COLOR = '#FF5722' # Deep Orange
ACCENT_GREEN = '#4CAF50' # Green
ACCENT_RED = '#E91E63' # Pink/Red
NEUTRAL_GRAY = '#607D8B' # Blue Gray

# Path to artifacts directory
ARTIFACT_DIR = r"C:\Users\khbik\.gemini\antigravity-ide\brain\68c85414-9e7d-4b89-ba7b-cc356eb204fa"

def generate_trader_pnl_chart(profiles_df):
    plt.figure(figsize=(10, 5))
    df_sorted = profiles_df.sort_values(by='Net_PnL', ascending=True)
    
    # Assign colors based on positive/negative
    colors = [ACCENT_GREEN if val > 0 else ACCENT_RED for val in df_sorted['Net_PnL']]
    
    # Shorten addresses for labels
    labels = [addr[:6] + "..." + addr[-4:] for addr in df_sorted['Account']]
    
    plt.barh(labels, df_sorted['Net_PnL'] / 1000.0, color=colors, alpha=0.9)
    plt.axvline(x=0, color='black', linewidth=0.8, linestyle='--')
    
    plt.title('Realized Net Profit/Loss (PnL) by Hyperliquid Trader Account', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Net PnL (in Thousands USD)', fontsize=10, labelpad=10)
    plt.ylabel('Trader Account (Truncated)', fontsize=10)
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(os.path.join(ARTIFACT_DIR, 'trader_pnl_distribution.png'), dpi=300)
    plt.close()
    print("Saved trader_pnl_distribution.png")

def generate_fgi_side_corr_chart(profiles_df):
    # Let's read the FGI Side Correlation computed in the analyze_correlation script.
    # To avoid repeating calculations, let's recalculate correlations here quickly
    df = pd.read_csv('merged_data.csv')
    df['Side_Val'] = np.where(df['Side'] == 'BUY', 1, -1)
    
    corrs = []
    for account, group in df.groupby('Account'):
        if len(group) > 50:
            corr = group['value'].corr(group['Side_Val'])
            net_pnl = profiles_df.loc[profiles_df['Account'] == account, 'Net_PnL'].values[0]
            prof_class = profiles_df.loc[profiles_df['Account'] == account, 'Profitability_Class'].values[0]
            corrs.append({
                'Account': account[:6] + "..." + account[-4:],
                'Corr': corr,
                'Profitability': prof_class,
                'Net_PnL': net_pnl
            })
            
    corrs_df = pd.DataFrame(corrs).sort_values(by='Net_PnL', ascending=True)
    
    plt.figure(figsize=(10, 5))
    colors = [PRIMARY_COLOR if p == 'Profitable' else SECONDARY_COLOR for p in corrs_df['Profitability']]
    
    plt.barh(corrs_df['Account'], corrs_df['Corr'], color=colors, alpha=0.9)
    plt.axvline(x=0, color='black', linewidth=0.8, linestyle='--')
    
    plt.title('Trader Sentiment-Direction Correlation (FGI vs Trade Side)\nNegative = Contrarian (Buy Fear), Positive = Herd/FOMO (Buy Greed)', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Pearson Correlation Coefficient', fontsize=10, labelpad=10)
    plt.ylabel('Trader Account', fontsize=10)
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=PRIMARY_COLOR, label='Profitable Trader (Avg Corr: -0.05)'),
        Patch(facecolor=SECONDARY_COLOR, label='Unprofitable Trader (Avg Corr: +0.17)')
    ]
    plt.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(ARTIFACT_DIR, 'sentiment_trader_correlation.png'), dpi=300)
    plt.close()
    print("Saved sentiment_trader_correlation.png")

def generate_behavior_by_sentiment_chart():
    df = pd.read_csv('detailed_sentiment_behavior.csv')
    sentiment_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
    
    prof_df = df[df['Profitability'] == 'Profitable'].set_index('Sentiment').reindex(sentiment_order)
    unprof_df = df[df['Profitability'] == 'Unprofitable'].set_index('Sentiment').reindex(sentiment_order)
    
    # Subplot 1: Buy Ratio
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    x = np.arange(len(sentiment_order))
    width = 0.35
    
    ax1.bar(x - width/2, prof_df['Buy_Ratio'], width, label='Profitable Traders', color=PRIMARY_COLOR, alpha=0.9)
    ax1.bar(x + width/2, unprof_df['Buy_Ratio'], width, label='Unprofitable Traders', color=SECONDARY_COLOR, alpha=0.9)
    ax1.axhline(y=0.5, color='gray', linestyle='--', linewidth=0.8)
    
    ax1.set_title('Buy Ratio (Percentage of BUY executions) by Sentiment', fontsize=11, fontweight='bold', pad=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(sentiment_order, rotation=15)
    ax1.set_ylabel('Buy Ratio (1.0 = 100% Buy)', fontsize=10)
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Subplot 2: Average Trade Size
    ax2.bar(x - width/2, prof_df['Avg_Size_USD'] / 1000.0, width, label='Profitable Traders', color=PRIMARY_COLOR, alpha=0.9)
    ax2.bar(x + width/2, unprof_df['Avg_Size_USD'] / 1000.0, width, label='Unprofitable Traders', color=SECONDARY_COLOR, alpha=0.9)
    
    ax2.set_title('Average Trade Execution Size by Sentiment', fontsize=11, fontweight='bold', pad=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(sentiment_order, rotation=15)
    ax2.set_ylabel('Average Trade Size (in Thousands USD)', fontsize=10)
    ax2.legend()
    ax2.grid(axis='y', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(ARTIFACT_DIR, 'behavior_by_sentiment.png'), dpi=300)
    plt.close()
    print("Saved behavior_by_sentiment.png")

def generate_backtest_chart():
    df = pd.read_csv('backtest_results.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['Cum_BuyHold'] - 1, label='Buy & Hold BTC', color='black', linewidth=1.5)
    plt.plot(df['date'], df['Cum_Contrarian_LongOnly'] - 1, label='Contrarian Long-Only (Buy Fear, Sell Greed)', color=PRIMARY_COLOR, linewidth=1.5)
    plt.plot(df['date'], df['Cum_Momentum'] - 1, label='Momentum/FOMO (Buy Greed, Sell Fear)', color=SECONDARY_COLOR, linewidth=1.5)
    plt.plot(df['date'], df['Cum_Contrarian_LS'] - 1, label='Contrarian Long-Short', color=ACCENT_RED, linestyle='--', linewidth=1.2)
    
    # Highlight Fear and Greed zones using FGI background shading or just keep it clean
    # Let's format y axis as percentage
    import matplotlib.ticker as mtick
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    
    plt.title('Backtest Cumulative Returns (Dec 4, 2023 - May 1, 2025)\nFear & Greed Index Strategies vs. BTC Buy & Hold', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Date', fontsize=10, labelpad=10)
    plt.ylabel('Cumulative Return (%)', fontsize=10)
    plt.legend(loc='upper left', frameon=True)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(os.path.join(ARTIFACT_DIR, 'backtest_cumulative_returns.png'), dpi=300)
    plt.close()
    print("Saved backtest_cumulative_returns.png")

if __name__ == '__main__':
    profiles = pd.read_csv('trader_profiles.csv')
    generate_trader_pnl_chart(profiles)
    generate_fgi_side_corr_chart(profiles)
    generate_behavior_by_sentiment_chart()
    generate_backtest_chart()
    print("All charts successfully generated!")
