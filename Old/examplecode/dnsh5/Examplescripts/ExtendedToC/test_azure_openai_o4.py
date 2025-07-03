import requests
import json

API_KEY = "ENGXrGuPdJiXrSyH55lYMcdM7EA6sA4s3sFW8Lkx8cjdv7MbzOntJQQJ99BEAC5RqLJXJ3w3AAAAACOGZE3q"
ENDPOINT = "https://o3-may25-resource.openai.azure.com/openai/deployments/o4-mini-ssgr/chat/completions?api-version=2025-01-01-preview"

headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}

user_question = input("Enter your question: ")

data = {
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_question}
    ],
    "max_completion_tokens": 100000
}

response = requests.post(ENDPOINT, headers=headers, data=json.dumps(data))

print("Status Code:", response.status_code)
try:
    resp_json = response.json()
    print("Response:", json.dumps(resp_json, indent=2))
except Exception as e:
    print("Failed to parse JSON response:", e)
    print(response.text) 