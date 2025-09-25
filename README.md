# Reddit-Stock-Data

## Project overview
This repository supports a presentation that explores how retail investor conversations line up with market performance. At a high level, we:

1. **Collect Reddit activity** – scrape posts and comments about a curated list of tickers from investing subreddits, store the raw text, and capture engagement metrics such as upvotes, comment counts, and awards.
2. **Enrich the market context** – pair each scraped discussion with historical pricing and volume data pulled for the same ticker and timeframe.
3. **Analyze the language** – apply natural language processing (VADER, topic modeling, and custom keyword scoring) to extract sentiment, momentum-related phrases, and recurring themes from the Reddit corpus.
4. **Compare narratives to price action** – line up the Reddit-derived signals with their corresponding market data to see where shifts in sentiment, attention, or topics precede or mirror stock movements.

## How the findings are presented
The final presentation walks through notable examples where Reddit buzz and market trends appear to overlap. Slides highlight:

- Heat maps of sentiment versus daily returns to illustrate alignment or divergence.
- Engagement spikes (e.g., comment surges, award bursts) before significant price moves.
- Word clouds and topic timelines that reveal how narratives evolve around major events.
- Case studies that blend the qualitative insights from Reddit with quantitative indicators from the market data.

## Repository contents
- **datacollection.py / DataCleaning.py** – scripts that handle scraping, data consolidation, and cleaning of Reddit activity.
- **sentiment_vs_market.py** – utilities for joining Reddit metrics to historical stock performance and generating comparative visuals.
- **CSDS312_Final_Data_Collection.ipynb** – a notebook that demonstrates the end-to-end workflow and produces artifacts for the presentation.
- **Hedonometer.csv**, `stocks_with_rating.csv`, and other CSVs – curated datasets used to calibrate sentiment baselines and store enriched results.

Feel free to adapt the pipeline for new tickers or forums. Updating the ticker list and rerunning the collection + cleaning scripts will refresh the inputs that feed the NLP analysis and downstream presentation materials.
