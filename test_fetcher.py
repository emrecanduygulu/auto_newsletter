from agents.fetcher import fetch_news

if __name__ == "__main__":
    articles = fetch_news("NBA") 
    for article in articles:
        print(f"🔹 {article['title']}")
        print(f"🔹 {article['description']}")
        print(f"🔹 {article['url']}")
        print("-" * 50)
