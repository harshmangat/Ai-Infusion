import os
from dotenv import load_dotenv
from openai import OpenAI
from scrapper import fetch_website_contents

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = OpenAI(api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
              )

system_prompt = """You analyze the contents of a website and
give a short, friendly summary. Ignore navigation menus.
Respond in markdown."""

def summarize(url):
    website=fetch_website_contents(url)

    result = client.chat.completions.create(
      model="openai/gpt-oss-20b",
      messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Summarize this website:\n\n{website}"}
      ],
    )
    return result.choices[0].message.content