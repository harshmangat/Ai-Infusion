import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()
embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="chroma_db", embedding_function=embedder)

key = os.getenv("GROQ_API_KEY")
if not key:
    raise RuntimeError("GROQ_API_KEY is missing from your .env file")



model = ChatOpenAI(
    model="openai/gpt-oss-20b",
    api_key=key,
    base_url="https://api.groq.com/openai/v1",
    temperature=0.0,
)

prompt = ChatPromptTemplate.from_template("""
Answer the question using ONLY the context below. If the context doesn't contain
the answer, say "I don't know." Be concise and quote facts directly.

Context:
{context}

Question: {question}
""")

def rag_answer(question):
    docs = db.similarity_search(question, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    chain = prompt | model
    res = chain.invoke({"context": context, "question": question}).content
    return res


print(rag_answer("what is the return policy?"))  # Output: "Our return policy allows refunds within 30 days of purchase."