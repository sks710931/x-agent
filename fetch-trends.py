import logging
import json
import time
import pandas as pd
import requests
from pytrends.request import TrendReq
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup

# 🔹 Set up logging
logging.basicConfig(filename="trend_search.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🔹 Expanded list of generic trends to ignore
GENERIC_TRENDS = {
    "news today", "latest news", "breaking news", "top news", "trending now", "current events",
    "live updates", "today’s headlines", "viral news", "important news",
    "hot topics", "biggest news", "daily news", "top stories",
    "sports news", "business news", "entertainment news", "stock market news",
    "weather update", "COVID update", "gold price today", "petrol price today",
    "political news", "technology news", "science news", "education news",
    "latest updates", "financial news", "global news", "Indian news",
    "Google news", "WhatsApp news", "YouTube trending", "trending searches",
    "India trends", "trending news in India"
}

# 🔹 Function to clean and modify search queries
def clean_trend(trend):
    trend_lower = trend.lower()
    if trend_lower in GENERIC_TRENDS:
        return None  # Ignore generic trends
    if "news" not in trend_lower:
        return f"{trend} news"  # Add "news" if not already present
    return trend  # Return as is if it already contains "news"

# 🔹 Function to search DuckDuckGo for a given query
def duckduckgo_search(query):
    search_results = []
    with DDGS() as ddgs:
        for result in ddgs.text(query, max_results=5):  # Fetch top 5 results
            search_results.append({"title": result["title"], "url": result["href"]})
    return search_results

# 🔹 Function to extract text from a webpage
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = " ".join([para.get_text() for para in paragraphs[:5]])  # Get first 5 paragraphs
            return text if text else "⚠️ No readable content found."
        else:
            return f"⚠️ Failed to fetch URL (Status Code: {response.status_code})"
    except Exception as e:
        return f"⚠️ Error fetching URL: {str(e)}"

# 🔹 Initialize pytrends API
pytrends = TrendReq()

# 🔹 Get trending searches in India
trending_searches = pytrends.trending_searches(pn="india")

# 🔹 Rename the first column to "Trending Topic"
trending_searches.columns = ["Trending Topic"]

# 🔹 Display raw trends
print("🔥 Raw Trending Topics in India:")
print(trending_searches.head(20))

# 🔹 Clean trends: Remove generic ones & modify others
filtered_trends = [clean_trend(trend) for trend in trending_searches["Trending Topic"][:20]]
filtered_trends = [t for t in filtered_trends if t is not None]  # Remove `None` values

# 🔹 Display filtered trends
print("\n🔥 Filtered & Optimized Trends:")
print(filtered_trends)

# 🔹 Save filtered trends to CSV
pd.DataFrame({"Trending Topic": filtered_trends}).to_csv("google_trends_india.csv", index=False)
print("✅ Filtered trends saved to google_trends_india.csv")

# 🔹 Storage list for automation processing
trend_data = []

# 🔹 Search Each Filtered Trend on DuckDuckGo & Extract Text
for trend in filtered_trends:
    print(f"\n🔍 Searching DuckDuckGo for: {trend}")
    logging.info(f"Searching DuckDuckGo for: {trend}")
    
    search_results = duckduckgo_search(trend)
    
    for i, result in enumerate(search_results):
        print(f"{i+1}. {result['title']} - {result['url']}")
        logging.info(f"Fetching URL: {result['url']}")

        # Extract text content from the URL
        extracted_text = extract_text_from_url(result["url"])
        print(f"\n📝 Extracted Text:\n{extracted_text[:1000]}...")  # Print first 1000 characters
        logging.info(f"Extracted Text: {extracted_text[:1000]}...")

        # 🔹 Store data for automation processing
        trend_data.append({
            "trend": trend,
            "search_result_title": result["title"],
            "search_result_url": result["url"],
            "extracted_text": extracted_text[:2000]  # Store first 2000 characters
        })

    # ✅ Respect ethical scraping limits (Avoid detection)
    time.sleep(3)  # Wait 2 seconds between requests

# 🔹 Save extracted data to JSON
with open("trend_search_results.json", "w", encoding="utf-8") as json_file:
    json.dump(trend_data, json_file, ensure_ascii=False, indent=4)
print("✅ Search results saved to trend_search_results.json")
