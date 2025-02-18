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

def load_news_summaries(file_path):
    """Reads summarized news trends from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def generate_tweets(trend_name, trend_summary):
    """Generates a one-liner engagement tweet and a Twitter thread using GPT-4o."""
    
    system_prompt = (
        "You are an AI assistant with a witty, sarcastic, and right-leaning nationalist persona. "
        "Your goal is to generate satirical, opinionated, and highly engaging tweets that resonate with an audience "
        "that values nationalism, cultural pride, and political sharpness.\n\n"
        "### Instructions for Writing Viral Tweets:\n"
        "- Be unapologetically opinionated – Don't shy away from strong takes.\n"
        "- Use witty sarcasm and humor – Mock hypocrisy, expose double standards, and make punchy statements.\n"
        "- Use cultural/nationalist references – Highlight pride in Indian values, heritage, and national strength.\n"
        "- Expose media/political bias – Call out hypocrisy in mainstream narratives.\n"
        "- Keep it tweet-friendly – Short, sharp, and engaging (limit to **280 characters**).\n"
        "- Use satire cleverly – Present issues in a humorous but impactful manner.\n"
        "- Leverage virality hooks – Use rhetorical questions, irony, and hyperbole.\n"
    )

    user_prompt_one_liner = (
        f"Write a one-liner tweet (under 280 characters) for engagement based on the news: '{trend_name}'\n\n"
        f"Summary: {trend_summary}"
    )

    user_prompt_thread = (
        f"Write a viral Twitter thread (up to 10 tweets) summarizing and commenting on this news: '{trend_name}'\n\n"
        f"Summary: {trend_summary}\n\n"
        "Make the thread engaging, sarcastic, witty, and hard-hitting. Each tweet must be under 280 characters."
    )

    # Generate the one-liner tweet
    response_one_liner = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt_one_liner}
        ],
        max_tokens=100
    )
    
    # Generate the Twitter thread
    response_thread = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt_thread}
        ],
        max_tokens=800
    )

    one_liner_tweet = response_one_liner.choices[0].message.content.strip()
    twitter_thread = response_thread.choices[0].message.content.strip().split("\n")

    return {"trend": trend_name, "one_liner": one_liner_tweet, "twitter_thread": twitter_thread}

def save_tweets_to_json(tweets_data, output_file):
    """Saves the tweets to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(tweets_data, file, ensure_ascii=False, indent=4)
    print(f"Generated tweets saved to {output_file}")

if __name__ == "__main__":
    # Load summarized news trends
    news_summaries = load_news_summaries("summary.json")

    # Store tweets trend-wise
    all_tweets = []

    for news in news_summaries:
        trend_name = news["trend"]
        trend_summary = news["summary"]
        print(f"Generating tweets for trend: {trend_name} ...")

        # Generate viral tweets
        tweet_data = generate_tweets(trend_name, trend_summary)

        # Store in list format
        all_tweets.append(tweet_data)

    # Save generated tweets to JSON file
    output_file = "viral_tweets.json"
    save_tweets_to_json(all_tweets, output_file)
