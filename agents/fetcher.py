# agents/fetcher.py

import requests
import os
from dotenv import load_dotenv

# Load .env variables (API keys)
load_dotenv()

# Get your NewsAPI key
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news(topic, max_articles):
    query = topic
    page_size = max_articles
    """
    Fetch news articles from NewsAPI based on a search query.
    Returns a list of articles (title, description, url).
    """
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&"
        f"pageSize={page_size}&"
        f"sortBy=publishedAt&"
        f"apiKey={NEWS_API_KEY}"
    )
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    articles = data.get("articles", [])
    results = []

    for article in articles:
        title = article.get("title")
        description = article.get("description")
        url = article.get("url")
        if title and description and url:
            results.append({
                "title": title,
                "description": description,
                "url": url
            })

    return results
