from mcp.mcp import MCP
from agents.fetcher import fetch_news
from agents.reddit_fetcher import fetch_reddit
from agents.summerizer import summarize_topic
import json
from datetime import date
from pathlib import Path
from utils.r2_uploader import upload_to_r2

import boto3
import os

# Helpers

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    )

def get_index(s3, bucket_name):
    try:
        obj = s3.get_object(Bucket=bucket_name, Key="index.json")
        return json.load(obj["Body"])
    except s3.exceptions.NoSuchKey:
        return []
    except Exception as e:
        print(f"⚠️ Failed to load index.json: {e}")
        return []

def put_index(s3, bucket_name, index_dates):
    body = json.dumps(sorted(index_dates)).encode("utf-8")
    s3.put_object(Bucket=bucket_name, Key="index.json", Body=body, ContentType="application/json")


def main():
    mcp = MCP()

    # if not mcp.should_generate_today():
    #     print("✅ Already generated today's summary.")
    #     return

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

    # Save locally
    output_path = Path("website/data") / f"{day_data['date']}.json"
    with open(output_path, "w") as f:
        json.dump(day_data, f, indent=2)

    print(f"✅ Saved: {output_path}")

    # Upload to R2
    upload_to_r2(output_path)

    # ✅ Update index.json in R2
    print("🌐 Updating index.json in R2")
    s3 = get_s3_client()
    bucket_name = os.environ["R2_BUCKET_NAME"]

    index_dates = get_index(s3, bucket_name)
    today = date.today().isoformat()

    if today not in index_dates:
        index_dates.append(today)
        put_index(s3, bucket_name, index_dates)
        print(f"✅ index.json updated in R2 with {today}")
    else:
        print(f"ℹ️ index.json already contains {today}")

    # Update history in MCP
    mcp.add_today_to_history()

if __name__ == "__main__":
    main()



