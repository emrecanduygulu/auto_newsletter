import json
from pathlib import Path
from datetime import date

class MCP:
    def __init__(self, base_path="mcp"):
        self.context_path = Path(base_path) / "context.json"
        self.history_path = Path(base_path) / "history.json"
        self.load_context()
        self.load_history()

    def load_context(self):
        with open(self.context_path) as f:
            self.context = json.load(f)

    def load_history(self):
        with open(self.history_path) as f:
            self.history = json.load(f)

    def should_generate_today(self):
        today = date.today().isoformat()
        return today not in self.history["days"]

    def add_today_to_history(self):
        today = date.today().isoformat()
        if today not in self.history["days"]:
            self.history["days"].append(today)
            self.history["last_generated"] = today
            self.save_history()

    def save_history(self):
        with open(self.history_path, "w") as f:
            json.dump(self.history, f, indent=2)

    def get_topics(self):
        return self.context["topics"]

    def get_summary_style(self):
        return self.context.get("summary_style", "brief")

    def get_max_articles(self):
        return self.context.get("max_articles_per_topic", 5)

    def get_summarizer_model(self):
        return self.context.get("summarizer", "gemini_flash_lite")
    
    def reddit_enabled(self):
        return self.context.get("reddit", {}).get("enabled", False)

    def get_subreddits(self):
        return self.context.get("reddit", {}).get("subreddits", [])

    def get_reddit_post_limit(self):
        return self.context.get("reddit", {}).get("posts_per_subreddit", 10)

    def get_reddit_only_topics(self):
        return self.context.get("reddit", {}).get("only_topics", [])
