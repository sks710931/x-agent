from pytrends.request import TrendReq
import pandas as pd
from duckduckgo_search import DDGS
import time

# 🔹 Function to search DuckDuckGo for a given query
def duckduckgo_search(query):
    search_results = []
    with DDGS() as ddgs:
        for result in ddgs.text(query, max_results=10):  # Get top 10 results
            search_results.append(f"{result['title']} - {result['href']}")
    return search_results

# 🔹 Initialize pytrends API
pytrends = TrendReq()

# 🔹 Get trending searches in India
trending_searches = pytrends.trending_searches(pn="india")

# 🔹 Rename the first column to "Trending Topic"
trending_searches.columns = ["Trending Topic"]

# 🔹 Display top trends
print("🔥 Trending Topics in India:")
print(trending_searches.head(25))

# 🔹 Save to CSV
trending_searches.to_csv("google_trends_india.csv", index=False)
print("✅ Trends saved to google_trends_india.csv")

# 🔹 Search Each Trend on DuckDuckGo
for trend in trending_searches["Trending Topic"][:10]:  # Searching top 10 trends
    print(f"\n🔍 Searching DuckDuckGo for: {trend}")
    results = duckduckgo_search(trend)
    
    for i, result in enumerate(results):
        print(f"{i+1}. {result}")

    # ✅ Respect ethical scraping limits (Avoid detection)
    time.sleep(1)  # Wait 1 second between requests
