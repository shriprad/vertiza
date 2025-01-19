import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')

try:
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt="Hello, world!",
        max_tokens=10
    )
    print("Response:", response)
except Exception as e:
    print("Error:", e)
