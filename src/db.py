import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "crypto_news.db"

def init_db():
    """Veritabanı ve tabloyu oluşturur"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # DÜZELTME: 'plot_score' sütununu buraya ekledik!
    c.execute('''
        CREATE TABLE IF NOT EXISTS news (
            link TEXT PRIMARY KEY,
            title TEXT,
            published TEXT,
            source TEXT,
            sentiment_label TEXT,
            sentiment_score REAL,
            plot_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_news(df):
    """Yeni haberleri veritabanına kaydeder"""
    if df.empty: return
    
    conn = sqlite3.connect(DB_NAME)
    
    # 'plot_score' sütununun DataFrame'de olup olmadığını kontrol et
    # Eğer yoksa (eski veri kaynaklı), hesapla
    if 'plot_score' not in df.columns:
         df['plot_score'] = df.apply(lambda x: x['sentiment_score'] if x['sentiment_label'] == 'positive' else -x['sentiment_score'] if x['sentiment_label'] == 'negative' else 0, axis=1)

    for _, row in df.iterrows():
        try:
            # DÜZELTME: INSERT komutuna plot_score eklendi
            conn.execute('''
                INSERT OR IGNORE INTO news (link, title, published, source, sentiment_label, sentiment_score, plot_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (row['link'], row['title'], str(row['published']), row['source'], row['sentiment_label'], row['sentiment_score'], row['plot_score']))
        except Exception as e:
            print(f"DB Error: {e}")
            
    conn.commit()
    conn.close()

def get_all_news():
    """Tüm geçmiş haberleri getirir"""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql("SELECT * FROM news ORDER BY published DESC", conn)
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()