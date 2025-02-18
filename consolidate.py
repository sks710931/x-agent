import json
from collections import defaultdict

def summarize_trends(input_file, output_file):
    """
    Reads a JSON file, groups data by trend, and summarizes extracted_text.
    
    Args:
    input_file (str): Path to input JSON file.
    output_file (str): Path to save the summarized JSON file.
    """
    
    # Load the JSON file
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Group data by trend and combine extracted_text
    trend_summary = defaultdict(lambda: {"search_result_titles": [], "search_result_urls": [], "summarized_text": ""})

    for entry in data:
        trend = entry["trend"]
        trend_summary[trend]["search_result_titles"].append(entry["search_result_title"])
        trend_summary[trend]["search_result_urls"].append(entry["search_result_url"])
        trend_summary[trend]["summarized_text"] += f"{len(trend_summary[trend]['search_result_titles'])}. {entry['extracted_text']}\n\n"

    # Convert the summarized data to a list of dictionaries
    summarized_trends = [{"trend": trend, **info} for trend, info in trend_summary.items()]

    # Save the summarized trends to a new JSON file
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(summarized_trends, file, ensure_ascii=False, indent=4)

    print(f"Summarized data saved to {output_file}")

# Example usage:
input_file = "trend_search_results.json"  # Replace with the actual path
output_file = "summarized_trends.json"   # Output file
summarize_trends(input_file, output_file)
