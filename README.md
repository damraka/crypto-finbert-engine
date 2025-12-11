# Real-Time Crypto Sentiment & Volatility Engine (FinBERT)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![AI Model](https://img.shields.io/badge/AI-FinBERT-yellow)

This project utilizes **FinBERT** (Financial NLP Model) to perform sentiment analysis on cryptocurrency news and correlates it with real-time price volatility. It unifies market sentiment and technical analysis (SMA) into a single, interactive dashboard for investors.

## Features

* **AI-Powered Analysis:** Classifies news as *Positive, Negative, or Neutral* using the FinBERT model.
* **Live Data Stream:** Real-time prices via Binance (CCXT) and breaking news via RSS feeds.
* **Data Persistence (SQLite):** Analyzed news is stored in a local database, ensuring no data loss on refresh.
* **Technical & Fundamental:** Visualizes news markers directly on price charts alongside SMA (20/50) indicators.
* **Interactive Dashboard:** A modern UI built with Streamlit and Plotly.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/damraka/crypto-finbert-engine.git](https://github.com/damraka/crypto-finbert-engine.git)
    cd crypto-finbert-engine
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## 📸 Screenshots

The application includes Price Action Charts, Sentiment Distribution (Pie Chart), and Word Clouds.

---
*Developed by Damra Kaan Aglamaz*

