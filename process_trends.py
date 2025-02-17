import json
import os
from transformers import pipeline

# 🔹 Load the JSON file with extracted data
input_file = "trend_search_results.json"
output_file = "trend_summaries.json"

# 🔹 Load JSON Data
if not os.path.exists(input_file):
    print(f"❌ Error: {input_file} not found!")
    exit()

with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# 🔹 Group text by trend name
trend_data = {}
for entry in data:
    trend = entry["trend"]
    if trend not in trend_data:
        trend_data[trend] = []
    trend_data[trend].append(entry["extracted_text"])

# 🔹 Initialize Summarization Model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# 🔹 Create summary for each trend
summaries = []
for trend, texts in trend_data.items():
    print(f"📢 Summarizing trend: {trend}")

    # Combine all text for a given trend
    combined_text = " ".join(texts)[:5000]  # Limit text length to avoid token overflow

    # Generate summary
    summary = summarizer(combined_text, max_length=250, min_length=50, do_sample=False)[0]["summary_text"]

    # Store summarized trend data
    summaries.append({"trend": trend, "summary": summary})
    print(summary)

# 🔹 Save summarized data to a new JSON file
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(summaries, file, ensure_ascii=False, indent=4)

print(f"✅ Summaries saved to {output_file}")
