import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob

# Load Reddit data and compute sentiment
df_reddit = pd.read_csv('/mnt/data/reddit_posts_combined_20250423_140014.csv')
df_reddit['date'] = pd.to_datetime(df_reddit['created_utc'])
df_reddit['text'] = df_reddit['title'].fillna('') + ' ' + df_reddit['selftext'].fillna('')
df_reddit['sentiment'] = df_reddit['text'].apply(lambda t: TextBlob(t).sentiment.polarity)

# Daily average sentiment and 7-day rolling
daily_sentiment = df_reddit.set_index('date')['sentiment'].resample('D').mean()
sentiment_7d = daily_sentiment.rolling(window=7, min_periods=1).mean()

# Load stock data and compute daily returns and 7-day rolling
df_stock = pd.read_csv('/mnt/data/final_stock_data.csv', parse_dates=['timestamp'])
daily_return = df_stock.set_index('timestamp')['close'].pct_change().resample('D').mean()
return_7d = daily_return.rolling(window=7, min_periods=1).mean()

# Merge for plotting
df_vis = pd.concat([sentiment_7d.rename('7d_sentiment'), return_7d.rename('7d_return')], axis=1).dropna()

# Plot cleaner dual-axis time series
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(df_vis.index, df_vis['7d_sentiment'], color='tab:orange', linewidth=2, label='7‑Day Avg Sentiment')
ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Sentiment (7‑Day Avg)', color='tab:orange', fontsize=12)
ax1.tick_params(axis='y', labelcolor='tab:orange')
ax1.grid(True, linestyle='--', alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(df_vis.index, df_vis['7d_return'], color='tab:blue', linewidth=2, label='7‑Day Avg Return')
ax2.set_ylabel('Return (7‑Day Avg %)', color='tab:blue', fontsize=12)
ax2.tick_params(axis='y', labelcolor='tab:blue')

# Legends
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='upper left', frameon=False)

# Title and layout
plt.title('7-Day Rolling Avg: Reddit Sentiment vs. Market Return', fontsize=14)
fig.tight_layout()
plt.show()
