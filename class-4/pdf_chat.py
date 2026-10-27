from langchain_community.document_loaders import PyPDFLoader
# Added: load uploaded HTML documents for HTML-to-text indexing.
from langchain_community.document_loaders import BSHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
# Added: detect whether the uploaded document is a PDF or HTML file.
from pathlib import Path
import os

# Added: load either PDF pages or HTML content before creating the vector index.
def build_index(document_path):
    file_extension = Path(document_path).suffix.lower()
    if file_extension == ".pdf":
        documents = PyPDFLoader(document_path).load()
    elif file_extension in {".html", ".htm"}:
        # Added: read HTML as UTF-8 instead of using Windows' cp1252 default.
        documents = BSHTMLLoader(document_path, open_encoding="utf-8").load()
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or HTML file.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )
    chunks = splitter.split_documents(documents)
    embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_documents(chunks, embedder,)
    return db


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

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
You are a helpful document assistant. Answer the question using ONLY the context below.
If the context doesn't contain the answer, say "I couldn't find that in the document."
After your answer, list the PDF page numbers or HTML file names used as sources.

Context:
{context}

Question: {question}
""")


def ask(db, question):
    docs = db.similarity_search(question, k=4)
    # Added: cite PDF page numbers when present and the HTML filename otherwise.
    context_parts = []
    for chunk in docs:
        page = chunk.metadata.get("page")
        if page is not None:
            source = f"page {page + 1}"
        else:
            source = f"file {Path(chunk.metadata.get('source', 'uploaded HTML')).name}"
        context_parts.append(f"[{source}] {chunk.page_content}")
    context = "\n\n".join(context_parts)
    chain = prompt | model
    res = chain.invoke({"context": context, "question": question}).content
    return res
