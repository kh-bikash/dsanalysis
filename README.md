# Hyperliquid Trader Performance vs. Market Sentiment Analysis

This repository contains the complete data science pipeline and report analyzing the relationship between historical trader performance on Hyperliquid and market sentiment (Bitcoin Fear and Greed Index). 

The goal of this assignment is to explore correlation patterns, identify behavioral biases (such as FOMO and panic selling), backtest trading strategies based on sentiment signals, and deliver actionable insights for Web3 trading.

---

## 📊 Quick Links
- **Detailed Report**: [report.md](report.md) — Includes complete tables, charts, and recommendations.
- **Charts Directory**: View generated visualizations directly in the repository:
  - [Trader PnL Distribution](trader_pnl_distribution.png)
  - [Buy Ratio & Trade Size by Sentiment](behavior_by_sentiment.png)
  - [Sentiment-Side Correlation (Contrarian vs. FOMO)](sentiment_trader_correlation.png)
  - [Backtest Cumulative Returns](backtest_cumulative_returns.png)

---

## 🛠️ Project Structure

### Data Files
- `fear_greed_index.csv`: Daily historical Fear and Greed Index data (2018–2025).
- `historical_data.csv`: High-frequency trader transaction log from Hyperliquid (211,224 executions, 32 unique accounts).
- `merged_data.csv` *(Generated)*: Aligned dataset linking trade times (converted from IST to UTC date) with daily sentiment index.
- `trader_profiles.csv` *(Generated)*: Performance metrics for each trader (PnL, Win Rate, Volume, classifications).
- `detailed_sentiment_behavior.csv` *(Generated)*: Grouped trader performance metrics by sentiment state.
- `btc_historical_prices.csv` *(Generated)*: Daily BTC-USD price history used for backtesting.
- `backtest_results.csv` *(Generated)*: Simulation data for various trading strategies.

### Python Code
- `preprocess.py`: Processes and merges execution timestamps with sentiment dates.
- `profile_traders.py`: Calculates trading metrics (realized return, fees, win rates) per account.
- `analyze_correlation.py`: Investigates statistical correlations between sentiment and trade sides.
- `analyze_behavior.py`: Extracts trade sizing and win-rate behaviors across sentiment classes.
- `fetch_btc_yfinance.py`: Programmatically pulls daily historical BTC prices.
- `backtest_strategy.py`: Simulates trading strategies and computes key metrics (annualized returns, Sharpe ratio, drawdowns) under 0.05% transaction fees.
- `optimize_backtest.py`: Grid-searches optimal FGI thresholds for maximum Sharpe ratio.
- `generate_charts.py`: Generates the figures embedded in the final report.

---

## 🚀 How to Run the Project

1. **Install Dependencies**:
   Ensure you have `pandas`, `numpy`, and `matplotlib` installed:
   ```bash
   pip install pandas numpy matplotlib requests
   ```

2. **Run Pipeline**:
   You can run the full analysis and generate all outputs and charts sequentially:
   ```bash
   # 1. Preprocess and merge data
   python preprocess.py
   
   # 2. Profile traders
   python profile_traders.py
   
   # 3. Analyze behaviors and correlations
   python analyze_correlation.py
   python analyze_behavior.py
   
   # 4. Fetch BTC prices & run backtests
   python fetch_btc_yfinance.py
   python backtest_strategy.py
   python optimize_backtest.py
   
   # 5. Generate report charts
   python generate_charts.py
   ```

---

## 💡 Top Findings Summary

1. **The Contrarian Edge**: Top profitable traders are contrarian (average negative correlation with sentiment). They buy fear and sell greed.
2. **The Herd Trap**: Unprofitable traders chase momentum (average positive correlation of `+0.17`). They buy during Greed (68% buy ratio) and panic sell during Fear (60% sell ratio).
3. **Sizing Folly**: Unprofitable traders trade with excessively large sizes during Fear ($14.6K avg size vs. $3.9K for profitable ones), attempting to catch falling knives without risk management.
4. **Strategy Optimization**: A simple strategy of buying BTC when the FGI is at/below Neutral ($\le 50$) and selling when it reaches Extreme Greed ($\ge 80$) **beats Buy & Hold BTC** over the backtest period:
   - **Optimized Strategy Return**: **143.05%** (vs 129.85% for Buy & Hold)
   - **Sharpe Ratio**: **2.11** (vs 1.53 for Buy & Hold)
   - **Max Drawdown**: **-26.55%** (vs -28.14% for Buy & Hold)
