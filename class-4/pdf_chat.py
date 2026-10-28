import hashlib
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import BSHTMLLoader, PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv(Path(__file__).parent.parent / ".env")

CHROMA_DIRECTORY = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "pdf_notes"

prompt = ChatPromptTemplate.from_template(
    """
You are a helpful notes assistant. Answer the question using only the supplied
context. If the context does not contain the answer, say
"I couldn't find that in the uploaded files."
After the answer, list the source filenames and PDF page numbers when available.

Context:
{context}

Question: {question}
"""
)


@lru_cache(maxsize=1)
def get_embedder():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def open_index(persist_directory=CHROMA_DIRECTORY):
    """Open the local persistent collection containing uploaded notes."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(persist_directory),
        embedding_function=get_embedder(),
    )


def _load_document(file_path):
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Uploaded file was not found: {path}")

    extension = path.suffix.lower()
    if extension == ".pdf":
        documents = PyPDFLoader(str(path)).load()
    elif extension in {".html", ".htm"}:
        documents = BSHTMLLoader(str(path), open_encoding="utf-8").load()
    else:
        raise ValueError(
            f"Unsupported file type for {path.name}. Upload PDF or HTML files."
        )

    if not documents or not any(document.page_content.strip() for document in documents):
        raise ValueError(f"No readable text was found in {path.name}.")

    file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    for document in documents:
        document.metadata["source_filename"] = path.name
        document.metadata["file_hash"] = file_hash

    return documents, file_hash


def build_index(document_paths, persist_directory=CHROMA_DIRECTORY):
    """Add one or more uploaded PDF/HTML files to the persistent Chroma index."""
    if not document_paths:
        raise ValueError("Upload at least one PDF or HTML file.")

    if isinstance(document_paths, (str, os.PathLike)):
        document_paths = [document_paths]

    all_documents = []
    file_names = []

    for file_path in document_paths:
        documents, file_hash = _load_document(file_path)
        all_documents.extend(documents)
        file_names.append(Path(file_path).name)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
    )
    chunks = splitter.split_documents(all_documents)
    if not chunks:
        raise ValueError("No readable text chunks were created from the uploaded files.")

    ids = []
    for chunk_number, chunk in enumerate(chunks):
        file_hash = chunk.metadata["file_hash"]
        chunk_hash = hashlib.sha256(chunk.page_content.encode("utf-8")).hexdigest()
        source_name = chunk.metadata["source_filename"]
        ids.append(
            hashlib.sha256(
                f"{file_hash}:{source_name}:{chunk_number}:{chunk_hash}".encode(
                    "utf-8"
                )
            ).hexdigest()
        )

    db = open_index(persist_directory)
    db.add_documents(chunks, ids=ids)
    return db, file_names, len(chunks)


@lru_cache(maxsize=1)
def get_model():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is missing from your .env file")

    return ChatOpenAI(
        model="openai/gpt-oss-20b",
        api_key=key,
        base_url="https://api.groq.com/openai/v1",
        temperature=0.0,
    )


def ask(db, question):
    if not question or not question.strip():
        raise ValueError("Enter a question about your uploaded files.")

    documents = db.similarity_search(question, k=8)
    if not documents:
        return "I couldn't find any indexed content. Upload PDF or HTML files first."

    context_parts = []
    for document in documents:
        filename = document.metadata.get("source_filename")
        if not filename:
            filename = Path(document.metadata.get("source", "uploaded file")).name

        page = document.metadata.get("page")
        source = f"{filename}, page {page + 1}" if page is not None else filename
        context_parts.append(f"[Source: {source}]\n{document.page_content}")

    chain = prompt | get_model()
    response = chain.invoke(
        {
            "context": "\n\n".join(context_parts),
            "question": question,
        }
    )
    return response.content
