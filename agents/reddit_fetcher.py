# agents/reddit_fetcher.py

import os
import praw
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Setup Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    user_agent=REDDIT_USER_AGENT
)

def fetch_reddit(subreddit_name, max_posts):
    """
    Fetch top daily posts from a given subreddit.
    Returns a list of posts (title, description, url).
    """
    subreddit = reddit.subreddit(subreddit_name)
    posts = []

    for post in subreddit.top(time_filter="day", limit=max_posts):
        if post.stickied or post.over_18:
            continue

        title = post.title
        description = post.selftext[:500] if post.selftext else ""
        url = post.url

        if title and url:
            posts.append({
                "title": title,
                "description": description,
                "url": url
            })

    return posts
