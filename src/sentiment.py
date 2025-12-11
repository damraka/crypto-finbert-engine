from transformers import pipeline
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd

# Pipeline definitio as a global variable.

def load_finbert():
    """
    Installs FinBERT model and tokenizer from HuggingFace.
    Loops pipeline object.
    """
    pipe = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    return pipe

def predict_sentiment(news_df, pipe):
    """
    Takes the news DataFrame, analyzes headlines for sentiment analysis
    and returns a new DataFrame with sentiment labels and scores.
    """
    if news_df.empty:
        return news_df

    titles = news_df['title'].tolist()
    
    # Inference
    results = pipe(titles)
    
    # Processing results
    labels = []
    scores = []
    plot_scores = [] # Numeric values for visualization

    for res in results:
        lbl = res['label']
        scr = res['score']
        
        labels.append(lbl)
        scores.append(scr)
        
        # Scoring for visualization:
        # Positive: +Score, Negative: -Score, Neutral: 0
        if lbl == 'positive':
            plot_scores.append(scr)
        elif lbl == 'negative':
            plot_scores.append(-scr)
        else:
            plot_scores.append(0)

    # Adding new columns to DataFrame
    news_df['sentiment_label'] = labels
    news_df['sentiment_score'] = scores
    news_df['plot_score'] = plot_scores
    
    return news_df



def generate_wordcloud(news_df):
    """
    Haber başlıklarından Kelime Bulutu oluşturur.
    """
    if news_df.empty:
        return None
        
    text = " ".join(news_df['title'].tolist())
    
    stopwords = ["to", "in", "for", "on", "of", "and", "the", "a", "is", "with", "at", "as", "be"]
    
    wordcloud = WordCloud(width=800, height=400, 
                          background_color='black', 
                          colormap='Greens',
                          stopwords=stopwords).generate(text)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    plt.close(fig)
    return fig