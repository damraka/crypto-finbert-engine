# src/config.py

# RSS resources to fetch cryptocurrency news
RSS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",             
    "https://theblock.co/rss",             
    "https://bitcoinmagazine.com/feed"     
]

# Crypto trading default settings
DEFAULT_SYMBOL = 'BTC/USDT'
TIMEFRAME = '4h'
LIMIT = 200