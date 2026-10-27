import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing from your .env file")


model = ChatOpenAI(model="openai/gpt-oss-20b",
    temperature=0.3,
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",)

# prompt = ChatPromptTemplate.from_template([
#     ("system", "You are a friendly assistant. Use the conversation history to stay consistent."),
#     MessagesPlaceholder("history"),
#     ("human", "{question}"),
# ])

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly assistant. Use the conversation history to stay consistent."),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])

chain = prompt | model

history = []                                 

print("Chat with the bot (type 'quit' to exit).")
while True:
    question = input("you: ")
    if question.strip().lower() in {"quit", "exit"}:
        break
    
    answer = chain.invoke({"history": history, "question": question}).content
    print("Bot:", answer)

    history.append((HumanMessage(question)))
    history.append((AIMessage(answer)))
    print(f"   (history now has {len(history)} messages)")