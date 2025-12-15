import feedparser
import pandas as pd
import ccxt
import logging
from src.config import RSS_FEEDS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_crypto_news():
    news_list = []
    logging.info("RSS feed taraması başladı...")
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                logging.warning(f"RSS Kaynağı boş veya erişilemedi: {url}")
                continue
                
            for entry in feed.entries[:5]:
                news_list.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'source': url.split('/')[2]
                })
        except Exception as e:
            logging.error(f"RSS Hatası ({url}): {e}")
            
    return pd.DataFrame(news_list)

def fetch_market_data(symbol, timeframe, limit):
    """
    Binance Cloud IP'lerini engellediği için Kraken kullanıyoruz.
    """
    try:
        exchange = ccxt.kraken()

        clean_symbol = symbol.replace('USDT', 'USD')
        
        ohlcv = exchange.fetch_ohlcv(clean_symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df
    except Exception as e:
        logging.error(f"Borsa Verisi Hatası (Kraken): {e}")

        return pd.DataFrame()