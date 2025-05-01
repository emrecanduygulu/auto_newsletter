from mcp.mcp import MCP
from agents.fetcher import fetch_news
from agents.reddit_fetcher import fetch_reddit
from agents.summerizer import summarize_topic
import json
from datetime import date
from pathlib import Path

def main():
    mcp = MCP()

  #  if not mcp.should_generate_today():
   #     print("✅ Already generated today's summary.")
    #    return

    news_topics = mcp.get_topics()
    news_limit = mcp.get_max_articles()
    style = mcp.get_summary_style()

    reddit_enabled = mcp.reddit_enabled()
    reddit_limit = mcp.get_reddit_post_limit()
    reddit_only_topics = mcp.get_reddit_only_topics()

    subreddit_mapping = {
        "NBA": "NBA",
        "AI": "ArtificialInteligence",
        "Gaming": "Gaming",
        "News": "news"
    }

    day_data = {
        "date": date.today().isoformat(),
        "topics": []
    }

    for topic in news_topics:
        articles = []

        if topic not in reddit_only_topics:
            print(f"🔍 Fetching NewsAPI: {topic}")
            news_articles = fetch_news(topic, news_limit)
            print(f"🗞️  {len(news_articles)} articles from NewsAPI")
            articles += news_articles

        if reddit_enabled:
            subreddit_name = subreddit_mapping.get(topic)
            if subreddit_name:
                try:
                    print(f"🔍 Fetching Reddit: {subreddit_name}")
                    reddit_articles = fetch_reddit(subreddit_name, reddit_limit)
                    print(f"👽 {len(reddit_articles)} articles from Reddit")
                    articles += reddit_articles
                except Exception as e:
                    print(f"❌ Reddit fetch failed for '{subreddit_name}': {e}")

        if not articles:
            print(f"⚠️  No articles found for topic: {topic}")
            continue

        print(f"🧠 Summarizing: {topic}")
        summary = summarize_topic(topic, articles, style)

        topic_block = {
            "name": topic,
            "summary": summary,
            "resources": [a["url"] for a in articles]
        }

        day_data["topics"].append(topic_block)

    output_path = Path("website/data") / f"{day_data['date']}.json"
    with open(output_path, "w") as f:
        json.dump(day_data, f, indent=2)

    print(f"✅ Saved: {output_path}")
    mcp.add_today_to_history()

if __name__ == "__main__":
    main()

