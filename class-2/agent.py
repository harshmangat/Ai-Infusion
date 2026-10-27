import json
import os
from urllib import response
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

PRICES = {"shoes": 799, "hat": 399, "bag": 1420, "shorts": 1299, "pants": 1699, "watch": 1999, "jacket": 2499, "socks": 199, "scarf": 299, "gloves": 499}

ITEMS = list(PRICES.keys())

WELCOME_MESSAGE = (
    f"Hi! I'm your shop assistant. \nI am new in this job 🙂 so please be patient. \nAsk me the price of any of this items:{ITEMS}. \nI promise I will learn other products soon 🤭"
)

def get_price(item):
    print(f"🔧 tool called: get_price({item})")
    return f"₹{PRICES.get(item.lower(), 'unknown')}"

tools = [{
    "type": "function",
    "function": {
        "name": "get_price",
        "description": "Get the price of a shop item the user asks about.",
        "parameters": {
            "type": "object",
            "properties": {"item": {"type": "string", "description": "the item name"}},
            "required": ["item"],
        },
    },
}]

def agent(user_message):
    messages =  [{"role": "user", "content": user_message}]

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b", messages=messages, tools=tools
    )
    msg = response.choices[0].message

    if msg.tool_calls:
        messages.append(msg)
        for call in msg.tool_calls:
          args = json.loads(call.function.arguments)
          result = get_price(args["item"])
          messages.append({
              "role": "tool",
              "tool_call_id": call.id,
              "content": result
          })

        response = client.chat.completions.create(
             model="openai/gpt-oss-20b", messages=messages)  

    return response.choices[0].message.content


if __name__ == "__main__":
    print(agent("What is the price of shoes?"))
    print("***")
    print(agent("Hi! What can you help with?"))    
