import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from src import config, data_loader, sentiment, db
import pandas as pd
import numpy as np
import logging

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Crypto FinBERT Pro (DB)", layout="wide", page_icon="🧠")

st.markdown("""
<style>
.big-font { font-size:20px !important; }
.metric-container { background-color: #1E1E1E; padding: 10px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("🧠 Crypto FinBERT: Persistent Sentiment Engine")

# --- INITIALIZE DATABASE ---
db.init_db()

# --- SIDEBAR ---
st.sidebar.header("⚙️ Control Panel")
symbol = st.sidebar.selectbox("Select Pair", ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'DOGE/USDT'])
timeframe = st.sidebar.selectbox("Timeframe", ['1h', '4h', '1d'], index=1)
limit = st.sidebar.slider("Number of Candles", 50, 500, 200)

st.sidebar.markdown("---")
st.sidebar.subheader("🧪 AI Sandbox")
user_text = st.sidebar.text_area("Test your own headline:", placeholder="E.g. Bitcoin hits new all time high!")
if st.sidebar.button("Analyze Text"):
    # Sandbox mantığı burada
    pass 

st.sidebar.markdown("---")
refresh = st.sidebar.button("🚀 Run Analysis & Update DB", use_container_width=True)

# --- MODEL LOADING ---
@st.cache_resource
def get_model():
    return sentiment.load_finbert()

with st.spinner("Initializing AI Core..."):
    pipe = get_model()

# Sandbox Process
if user_text:
    res = sentiment.predict_sentiment(pd.DataFrame([{'title': user_text}]), pipe)
    lbl = res.iloc[0]['sentiment_label']
    scr = res.iloc[0]['sentiment_score']
    color = "green" if lbl == 'positive' else "red" if lbl == 'negative' else "gray"
    st.sidebar.markdown(f"Result: :{color}[**{lbl.upper()}**] ({scr:.2f})")

# --- HELPER FUNCTIONS ---
def calculate_correlation(df_price, df_news):
    if df_news.empty or df_price.empty: return 0
    df_news['merged_time'] = pd.to_datetime(df_news['published']).dt.floor('h')
    df_price['merged_time'] = pd.to_datetime(df_price['timestamp']).dt.floor('h')
    merged = pd.merge(df_price, df_news, on='merged_time', how='inner')
    
    if len(merged) > 2:
        return merged['close'].corr(merged['plot_score'])
    return 0

# --- MAIN APP LOGIC ---

# 1. DATA HANDLING
with st.spinner('Syncing with Database & Exchange...'):
    df_price = data_loader.fetch_market_data(symbol, timeframe, limit)
    if not df_price.empty:
        df_price['timestamp'] = pd.to_datetime(df_price['timestamp'], unit='ms', utc=True)

    df_news = db.get_all_news()

    if df_news.empty or refresh:
        if df_news.empty:
            st.info("Veritabanı boş, ilk kurulum için veriler çekiliyor...")
        new_news = data_loader.fetch_crypto_news()
        if not new_news.empty:
            analyzed_news = sentiment.predict_sentiment(new_news, pipe)
            db.save_news(analyzed_news) # Kaydet
            
            df_news = db.get_all_news() 
            st.toast(f"Database updated with {len(new_news)} new articles!", icon="💾")
    

    if not df_news.empty:
        df_news['published'] = pd.to_datetime(df_news['published'], utc=True)

# --- DASHBOARD RENDERING ---

# KPI METRICS
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
current_price = df_price['close'].iloc[-1] if not df_price.empty else 0
price_change = (df_price['close'].iloc[-1] - df_price['open'].iloc[0]) if not df_price.empty else 0
avg_sentiment = df_news['plot_score'].mean() if not df_news.empty else 0

with col_m1: st.metric("Current Price", f"${current_price:,.2f}", f"{price_change:,.2f}")
with col_m2: 
    sentiment_delta = "Bullish" if avg_sentiment > 0.1 else "Bearish" if avg_sentiment < -0.1 else "Neutral"
    st.metric("Market Sentiment (DB)", f"{avg_sentiment:.3f}", sentiment_delta)
with col_m3: st.metric("Total News in DB", len(df_news))
with col_m4:
    corr = calculate_correlation(df_price, df_news)
    st.metric("Correlation", f"{corr:.2f}")

# TABS
tab1, tab2, tab3 = st.tabs(["📈 Price & Signals", "📊 Sentiment Analytics", "☁️ Word Cloud"])

with tab1:
    if not df_price.empty:
        df_price['SMA_20'] = df_price['close'].rolling(window=20).mean()
        df_price['SMA_50'] = df_price['close'].rolling(window=50).mean()

        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df_price['timestamp'], open=df_price['open'], high=df_price['high'], low=df_price['low'], close=df_price['close'], name='Price'))
        fig.add_trace(go.Scatter(x=df_price['timestamp'], y=df_price['SMA_20'], line=dict(color='yellow', width=1), name='SMA 20'))
        fig.add_trace(go.Scatter(x=df_price['timestamp'], y=df_price['SMA_50'], line=dict(color='cyan', width=1), name='SMA 50'))
        
        if not df_news.empty:
            # Sadece grafiğin zaman aralığındaki haberleri göster
            min_date = df_price['timestamp'].min()
            rel_news = df_news[df_news['published'] >= min_date]
            
            pos = rel_news[rel_news['sentiment_label'] == 'positive']
            fig.add_trace(go.Scatter(x=pos['published'], y=[df_price['high'].max()]*len(pos), mode='markers', marker=dict(symbol='triangle-up', size=13, color='#00FF00'), name='Positive', hovertext=pos['title']))
            
            neg = rel_news[rel_news['sentiment_label'] == 'negative']
            fig.add_trace(go.Scatter(x=neg['published'], y=[df_price['low'].min()]*len(neg), mode='markers', marker=dict(symbol='triangle-down', size=13, color='#FF0000'), name='Negative', hovertext=neg['title']))
        
        fig.update_layout(height=500, template="plotly_dark", title=f"{symbol} Price Action & Sentiment")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.subheader("Sentiment Distribution")
        if not df_news.empty:
            pie_fig = px.pie(df_news, names='sentiment_label', title='Database Sentiment Ratio', 
                             color='sentiment_label',
                             color_discrete_map={'positive':'green', 'negative':'red', 'neutral':'gray'})
            st.plotly_chart(pie_fig, use_container_width=True)
    with col_a2:
        st.subheader("Sentiment Trend")
        if not df_news.empty:
            df_news_sorted = df_news.sort_values('published')
            df_news_sorted['rolling_sent'] = df_news_sorted['plot_score'].rolling(window=10).mean()
            line_fig = px.line(df_news_sorted, x='published', y='rolling_sent', title='Moving Average Sentiment')
            line_fig.add_hline(y=0, line_dash="dash", line_color="white")
            st.plotly_chart(line_fig, use_container_width=True)

with tab3:
    if not df_news.empty:
        wc_fig = sentiment.generate_wordcloud(df_news)
        if wc_fig: st.pyplot(wc_fig)
    else: st.warning("No data for Word Cloud")

# NEWS LIST
st.markdown("### 📰 News History (From Database)")
if not df_news.empty:
    for _, row in df_news.head(6).iterrows():
        color = "#00FF00" if row['sentiment_label'] == 'positive' else "#FF0000" if row['sentiment_label'] == 'negative' else "#808080"
        icon = "🚀" if row['sentiment_label'] == 'positive' else "📉" if row['sentiment_label'] == 'negative' else "😐"
        st.markdown(f"""
        <div style="border-left: 4px solid {color}; padding-left: 10px; margin-bottom: 8px; background-color: #262730; border-radius: 5px; padding: 8px;">
            <small style="color: #aaa;">{row['published'].strftime('%Y-%m-%d %H:%M')} | {row['source']}</small><br>
            <span style="font-weight:600">{row['title']}</span><br>
            <span style="color: {color}; font-size: 0.9em;">{icon} {row['sentiment_label'].upper()} ({row['sentiment_score']:.2f})</span>
        </div>
        """, unsafe_allow_html=True)