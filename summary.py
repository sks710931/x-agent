import json
import openai

# Azure OpenAI Configuration
API_KEY = "Ab5GPoC9x4hTAmf8MJSGRWadYIMjLmHhyAevQedpU1klEa4EOKDqJQQJ99BBAC4f1cMXJ3w3AAAAACOGD5AM"
AZURE_ENDPOINT = "https://deepseek2392328626.services.ai.azure.com"
DEPLOYMENT_NAME = "gpt-4o"

openai.api_key = API_KEY
openai.api_base = AZURE_ENDPOINT

# Initialize Azure OpenAI Client
client = openai.AzureOpenAI(
    api_key=API_KEY,  
    azure_endpoint=AZURE_ENDPOINT,
    api_version="2024-08-01-preview"
)

def load_summarized_trends(file_path):
    """Reads summarized trends from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def summarize_trend_with_gpt4o(trend_name, trend_text):
    """Sends a single trend summary to GPT-4o for a concise summary."""
    
    system_prompt = (
        "You are a professional news summarizer. Your task is to take multiple news summaries "
        "from different sources under a given trend and condense them into a well-structured, concise report. "
        "Ensure accuracy, coherence, and neutrality in your summarization."
    )

    user_prompt = f"Summarize the following news articles under the trend '{trend_name}' concisely:\n\n{trend_text}"

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,  
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=500
    )

    return response.choices[0].message.content

def save_trend_wise_summary(trend_summaries, output_file):
    """Saves the summarized news trend-wise to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(trend_summaries, file, ensure_ascii=False, indent=4)
    print(f"Trend-wise news summary saved to {output_file}")

if __name__ == "__main__":
    # Load summarized news trends
    summarized_trends = load_summarized_trends("summarized_trends.json")

    # Store summarized news trend-wise
    trend_wise_summaries = []

    for trend in summarized_trends:
        trend_name = trend["trend"]
        trend_text = trend["summarized_text"]
        print(f"Summarizing trend: {trend_name} ...")
        
        # Get concise summary for each trend
        concise_summary = summarize_trend_with_gpt4o(trend_name, trend_text)
        
        # Store in list format
        trend_wise_summaries.append({"trend": trend_name, "summary": concise_summary})

    # Save trend-wise summary to JSON file
    output_file = "summary.json"
    save_trend_wise_summary(trend_wise_summaries, output_file)
