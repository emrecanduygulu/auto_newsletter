from mcp.mcp import MCP
from agents.fetcher import fetch_news
from agents.summerizer import summarize_topic
import json
from datetime import date
from pathlib import Path

def main():
    mcp = MCP()

    if not mcp.should_generate_today():
        print("✅ Already generated today's summary.")
        return

    topics = mcp.get_topics()
    style = mcp.get_summary_style()
    max_articles = mcp.get_max_articles()

    day_data = {
        "date": date.today().isoformat(),
        "topics": []
    }

    for topic in topics:
        print(f"🔍 Fetching: {topic}")
        articles = fetch_news(topic, max_articles)

        print(f"🧠 Summarizing: {topic}")
        summary = summarize_topic(topic, articles, style)

        topic_block = {
            "name": topic,
            "summary": summary,
            "resources": [a['url'] for a in articles]
        }

        day_data["topics"].append(topic_block)

    # Save JSON to website/data
    output_path = Path("website/data") / f"{day_data['date']}.json"
    with open(output_path, "w") as f:
        json.dump(day_data, f, indent=2)

    print(f"✅ Saved: {output_path}")
    mcp.add_today_to_history()

if __name__ == "__main__":
    main()
