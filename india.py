import logging
import json
import time
import requests
import openai
import pandas as pd
from pytrends.request import TrendReq
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup

# 🔹 Logging Setup
logging.basicConfig(
    filename="trend_search.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 🔹 Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "7642500985:AAFqfcSW9toBj-Toym-ZE0IhG-JKnCb9YAs"
TELEGRAM_CHAT_ID = "1159940939"

# 🔹 OpenAI Configuration
API_KEY = "BGQ1A7bgwLggT487YSjkHuQdmo49Wnc40MWesDlBHyGLpNCGFibCJQQJ99BBACYeBjFXJ3w3AAAAACOGi0yh"
AZURE_ENDPOINT = "https://octofoundry6733257025.cognitiveservices.azure.com"
DEPLOYMENT_NAME = "gpt-4o"

openai.api_key = API_KEY
openai.api_base = AZURE_ENDPOINT

client = openai.AzureOpenAI(
    api_key=API_KEY,  
    azure_endpoint=AZURE_ENDPOINT,
    api_version="2024-08-01-preview"
)

# 🔹 Google Trends Initialization
pytrends = TrendReq()

# 🔹 Function to search DuckDuckGo
def duckduckgo_search(query):
    print(f"🔍 Searching DuckDuckGo for: {query}")
    logging.info(f"Searching DuckDuckGo for: {query}")
    
    search_results = []
    try:
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=5):
                search_results.append({"title": result["title"], "url": result["href"]})
    except Exception as e:
        print(f"⚠️ Error searching DuckDuckGo for '{query}': {e}")
        logging.error(f"Error searching DuckDuckGo for '{query}': {e}")
    
    return search_results

# 🔹 Function to extract text from a webpage
def extract_text_from_url(url):
    print(f"📰 Extracting content from: {url}")
    logging.info(f"Extracting content from: {url}")
    
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = " ".join([para.get_text() for para in paragraphs[:5]])
            return text if text else "⚠️ No readable content found."
        else:
            return f"⚠️ Failed to fetch URL (Status Code: {response.status_code})"
    except Exception as e:
        return f"⚠️ Error fetching URL: {str(e)}"

# 🔹 Function to summarize trends using GPT-4o
def summarize_trend_with_gpt4o(trend_name, trend_text):
    print(f"✍️ Summarizing trend: {trend_name}")
    logging.info(f"Summarizing trend: {trend_name}")

    system_prompt = "You are a professional news summarizer. Summarize news articles into concise, well-structured reports."
    user_prompt = f"Summarize the following news articles under the trend '{trend_name}' concisely:\n\n{trend_text}"

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,  
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Error summarizing trend '{trend_name}': {e}")
        logging.error(f"Error summarizing trend '{trend_name}': {e}")
        return "⚠️ Summary unavailable due to API error."

# 🔹 Function to generate tweets using GPT-4o
def generate_tweets(trend_name, trend_summary):
    print(f"🐦 Generating tweets for: {trend_name}")
    logging.info(f"Generating tweets for: {trend_name}")

    system_prompt = (
    "You are an Indian AI assistant with an opinionated and right-leaning nationalist persona. "
    "Your goal is to generate highly engaging tweets that resonate with an Indian audience "
    "that values nationalism, cultural pride, and political sharpness.\n\n"
    "### Instructions for Writing Viral Tweets:\n"
    "- Be unapologetically opinionated – Provide strong takes on trending topics.\n"
    "- Focus on **sharp, direct** messaging rather than excessive humor.\n"
    "- Use **cultural/nationalist references** – Highlight India's values, heritage, and national strength.\n"
    "- Expose **media/political bias** – Critically analyze mainstream narratives.\n"
    "- Keep it tweet-friendly – Short, **powerful, and engaging** (limit to **280 characters** for threads and **600 characters** for one-liners).\n"
    "- Use **virality hooks** – rhetorical questions, irony, and strong punchlines.\n"
    "- **Minimize excessive sarcasm** – Use it only when necessary to expose double standards.\n"
    "- Use Hinglish words along with **GenZ slang** whenever relevant.\n"
    "- Include **hashtags and emojis** to enhance engagement while keeping the tone serious and compelling.\n"
    "- **DO NOT** generate any tweets based on information beyond **October 2023**.\n"
    "- **DO NOT assume additional details** beyond what is provided in the extracted news articles.\n"
    "- **Ensure accuracy** – If the provided data lacks context, state that instead of making assumptions.\n"
    )

    user_prompt_one_liner = f"Write a one-liner tweet for '{trend_name}'. Summary: {trend_summary}"
    user_prompt_thread = f"Write a viral Twitter thread for '{trend_name}'. Summary: {trend_summary}"

    try:
        response_one_liner = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt_one_liner}],
            max_tokens=100
        )

        response_thread = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt_thread}],
            max_tokens=800
        )

        one_liner_tweet = response_one_liner.choices[0].message.content.strip()
        twitter_thread = response_thread.choices[0].message.content.strip().split("\n")

        return {"trend": trend_name, "one_liner": one_liner_tweet, "twitter_thread": twitter_thread}
    
    except Exception as e:
        print(f"⚠️ Error generating tweets for '{trend_name}': {e}")
        logging.error(f"Error generating tweets for '{trend_name}': {e}")
        return {"trend": trend_name, "one_liner": "⚠️ Failed to generate tweet.", "twitter_thread": ["⚠️ Failed to generate thread."]}

def send_md_to_telegram():
    print(f"📩 Sending viral_tweets.md to Telegram...")
    logging.info(f"Sending viral_tweets.md to Telegram...")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open("viral_tweets.md", "rb") as file:
        files = {"document": file}
        data = {"chat_id": TELEGRAM_CHAT_ID, "caption": "📜 Latest viral tweets report"}
        
        try:
            response = requests.post(url, data=data, files=files)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Error sending Markdown file to Telegram: {e}")
            logging.error(f"Error sending Markdown file to Telegram: {e}")
            return False
        
# 🔹 Main Function
if __name__ == "__main__":
    print("🚀 Fetching top trending topics in India...")
    logging.info("Fetching top trending topics in India...")

    trending_searches = pytrends.trending_searches(pn="india")
    trending_searches.columns = ["Trending Topic"]
    filtered_trends = [f"{trend} news" for trend in trending_searches["Trending Topic"][:10]]

    print(f"✅ Filtered Trends: {filtered_trends}")
    logging.info(f"Filtered Trends: {filtered_trends}")

    # Fetch articles and extract content
    trend_data = []
    for trend in filtered_trends:
        search_results = duckduckgo_search(trend)
        extracted_texts = [extract_text_from_url(result["url"]) for result in search_results]
        trend_data.append({"trend": trend, "extracted_text": " ".join(extracted_texts)})

    # Summarize the news
    summarized_trends = [{"trend": t["trend"], "summary": summarize_trend_with_gpt4o(t["trend"], t["extracted_text"])} for t in trend_data]

    # Generate tweets
    all_tweets = [generate_tweets(t["trend"], t["summary"]) for t in summarized_trends]

    # Save tweets to a Markdown file
    with open("viral_tweets.md", "w", encoding="utf-8") as file:
        for tweet in all_tweets:
            file.write(f"## {tweet['trend']}\n")
            file.write(f"**One-liner Tweet:** {tweet['one_liner']}\n\n")
            file.write("### Twitter Thread:\n")
            for thread_tweet in tweet["twitter_thread"]:
                file.write(f"{thread_tweet}\n")
            file.write("\n---\n\n")

    # Send Markdown file to Telegram
    send_md_to_telegram()

    print("✅ All tweets saved to viral_tweets.md and sent to Telegram!")