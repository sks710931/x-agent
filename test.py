import openai

API_KEY = "Ab5GPoC9x4hTAmf8MJSGRWadYIMjLmHhyAevQedpU1klEa4EOKDqJQQJ99BBAC4f1cMXJ3w3AAAAACOGD5AM"
AZURE_ENDPOINT = "https://deepseek2392328626.services.ai.azure.com"
DEPLOYMENT_NAME = "gpt-4o"

openai.api_key = API_KEY
openai.api_base = AZURE_ENDPOINT


client = openai.AzureOpenAI(
    api_key=API_KEY,  
    azure_endpoint=AZURE_ENDPOINT,
    api_version="2024-08-01-preview"
)

response = client.chat.completions.create(
    model=DEPLOYMENT_NAME,  # Corrected model parameter
    messages=[{"role": "user", "content": "Summarize the latest news in India."}],
    max_tokens=100
)

print(response.choices[0].message.content)