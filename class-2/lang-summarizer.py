import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from scrapper import fetch_website_contents


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing from your .env file")

prompt = ChatPromptTemplate.from_template(
    "Give a short, friendly summary of this website:\n\n{website}"
)

# Use the Groq API for the model instead of OpenAI's API & this is client can say (model)
model = ChatOpenAI(
    model="openai/gpt-oss-20b",
    temperature=0.3,
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

parser = StrOutputParser()

chain = prompt | model | parser

def summarize(url):
    return chain.invoke({"website": fetch_website_contents(url)})

if __name__ == "__main__":
    print(summarize("https://www.python.org/"))