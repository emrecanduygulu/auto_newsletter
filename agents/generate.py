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


# =========================
# R2 / S3 helpers
# =========================

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name=os.environ.get("R2_REGION", "auto"),
    )


def list_all_json_dates(s3, bucket_name: str):
    """Bucket'taki tüm yyyy-mm-dd.json dosyalarını okuyup tarih listesi döndürür (index.json hariç)."""
    dates = []
    token = None

    while True:
        kwargs = {"Bucket": bucket_name}
        if token:
            kwargs["ContinuationToken"] = token

        resp = s3.list_objects_v2(**kwargs)
        for obj in resp.get("Contents", []):
            key = obj["Key"]
            if key == "index.json":
                continue
            if key.endswith(".json"):
                # "2025-08-12.json" -> "2025-08-12"
                date_str = key[:-5]
                # basit format kontrolü
                if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
                    dates.append(date_str)

        if resp.get("IsTruncated"):
            token = resp.get("NextContinuationToken")
        else:
            break

    # tekilleştir + sırala (yeni→eskiyi front-end'te ters çevirebilirsin)
    return sorted(set(dates))


def put_index(s3, bucket_name: str, index_dates: list[str]):
    body = json.dumps(index_dates, indent=2).encode("utf-8")
    s3.put_object(
        Bucket=bucket_name,
        Key="index.json",
        Body=body,
        ContentType="application/json",
    )
    print(f"✅ index.json written with {len(index_dates)} entries")


# =========================
# Main generation logic
# =========================

def main():
    mcp = MCP()

    news_topics = mcp.get_topics()
    news_limit = mcp.get_max_articles()
    style = mcp.get_summary_style()

    reddit_enabled = mcp.reddit_enabled()
    reddit_limit = mcp.get_reddit_post_limit()
    reddit_only_topics = mcp.get_reddit_only_topics()

    # konu -> subreddit eşleşmesi (senin projendeki isimlerle tutarlı)
    subreddit_mapping = {
        "NBA": "NBA",
        "AI": "ArtificialInteligence",  # subredditte tek L
        "Gaming": "Gaming",
        "News": "news",
    }

    today_str = date.today().isoformat()

    day_data = {
        "date": today_str,
        "topics": []
    }

    for topic in news_topics:
        articles = []

        # Reddit-only olmayan konularda NewsAPI
        if topic not in reddit_only_topics:
            print(f"🔍 Fetching NewsAPI: {topic}")
            news_articles = fetch_news(topic, news_limit)
            print(f"🗞️  {len(news_articles)} articles from NewsAPI")
            articles += news_articles

        # Reddit açıksa, eşleşen subreddit'ten çek
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
            print(f"⚠️ No articles found for topic: {topic}")
            continue

        print(f"🧠 Summarizing: {topic}")
        summary = summarize_topic(topic, articles, style)

        day_data["topics"].append({
            "name": topic,
            "summary": summary,
            "resources": [a["url"] for a in articles]
        })

    # Local kaydet (Actions log/debug ve olası tekrar upload için işine yarıyor)
    output_path = Path("website/data") / f"{today_str}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(day_data, f, indent=2)
    print(f"✅ Saved: {output_path}")

    # R2'ye gün dosyasını yükle
    upload_to_r2(output_path)

    # ✅ Self-healing index: bucket'ı gez, index.json'ı baştan yaz
    print("🧭 Rebuilding index.json from bucket listing…")
    s3 = get_s3_client()
    bucket_name = os.environ["R2_BUCKET_NAME"]
    index_dates = list_all_json_dates(s3, bucket_name)
    put_index(s3, bucket_name, index_dates)
    print("✅ index.json updated in R2")

    # MCP history
    mcp.add_today_to_history()


if __name__ == "__main__":
    main()

