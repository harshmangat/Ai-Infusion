import os
import langchain
print("LangChain version:", langchain.__version__)

from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import init_chat_model

load_dotenv(find_dotenv(), override=True)

PROVIDER = "groq"

if PROVIDER == "groq":
    MODEL = "openai/gpt-oss-20b"   # check console.groq.com for current IDs
    REQUIRED_KEY = "GROQ_API_KEY"
elif PROVIDER == "gemini":
    MODEL = "google_genai:gemini-3.8-flash"
    REQUIRED_KEY = "GEMINI_API_KEY"  




key = os.environ.get(REQUIRED_KEY)
if not key:
    raise SystemExit(
        f"{REQUIRED_KEY} not found in environment. "
        f"Add it to your .env for provider '{PROVIDER}'."
    )

print(f"Provider={PROVIDER}  Model={MODEL}  Key={key[:6]}...{key[-4:]}")

chat_model = init_chat_model(
    model=MODEL,
    model_provider=PROVIDER,
    api_key=key,
)


def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"The weather in {city} is sunny, 28 degrees C."""



from langchain.agents import create_agent

agent =  create_agent(
    model = chat_model,
    tools = [get_weather],
    system_prompt = (
        "You are a helpful assistant. Use the available tools when needed. "
        "Always state the final result clearly and completely in your answer."
    ),
)


def ask(question: str, show_steps: bool = True) -> None:
    response = agent.invoke({"messages": {"role": "user", "content": question}})
    print(f"\nQ: {question}")

    if show_steps:
        for msg in response["messages"]:
            if msg.type == "ai" and getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    print(f" [tool call]  {tc['name']}({tc['args']})")
            elif msg.type == "tool":
                print(f" [tool result] {msg.content}")

    print(f"A: {response['messages'][-1].content}")     


if __name__ == "__main__":
    ask("What is the weather in New York?") 
    ask("what is the capital of India?")



