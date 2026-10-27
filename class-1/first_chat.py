import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# create a wrapper of the openai client using the api key from the .env file
client = OpenAI(api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
             )

result = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        
      # {"role": "system", "content": "You are a angry travel guide"},
        {"role": "user", "content": "Suggest one thing to do in Bangalore"}
    ],
    temperature=2,
)

print(result.choices[0].message.content)