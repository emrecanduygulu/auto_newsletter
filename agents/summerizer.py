import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Get your Gemini API key from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure the Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)

# Load the Gemini model 
model = genai.GenerativeModel("gemini-2.0-flash-lite")  # Flash Lite alias

def summarize_article(title, description):
    """
    Use Gemini to summarize a news article into 2 crisp sentences.
    """
    prompt = f"""You are an expert newsletter writer. Summarize this article in 2 clear, short sentences for a daily newsletter. Only use what's relevant.

Title: {title}
Description: {description}

Summary:"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Summary error: {e}]"
    
def summarize_topic(topic, articles, style="brief"):
    combined = ""
    for article in articles:
        combined += f"Title: {article['title']}\n"
        combined += f"Description: {article['description']}\n\n"

    prompt = f"""You are an expert newsletter writer.
Summarize the following {len(articles)} articles about "{topic}" in a {style} style.
Use only relevant details. Return 2-3 clean sentences.

{combined}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Summary error: {e}]"
