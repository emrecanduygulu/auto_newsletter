from agents.fetcher import fetch_news
from agents.summarizer import summarize_article

if __name__ == "__main__":
    articles = fetch_news("NBA")
    for article in articles:
        print(f"📰 {article['title']}")
        summary = summarize_article(article['title'], article['description'])
        print(f"📌 {summary}")
        print(f"🔗 {article['url']}")
        print("-" * 60)

