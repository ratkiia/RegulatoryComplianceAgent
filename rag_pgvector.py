import os
from typing import List
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from pypdf import PdfReader
"""
rag_pgvector.py

This module is responsible for:
- Connecting to PostgreSQL with pgvector
- Ingesting regulatory documents (CT, NY, CA)
- Creating a retriever for downstream agents
"""

# Load environment variables from .env file
load_dotenv()

# Connection string for PostgreSQL with pgvector
PG_CONN_STR = os.getenv("PG_CONN_STR")

# Embedding model (OpenAI, modern text-embedding-3-small)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Vector store backed by PostgreSQL + pgvector
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="regulatory_embeddings",  # logical collection name
    connection=PG_CONN_STR,
    use_jsonb=True,  # store metadata as JSONB
)

# Text splitter to break long regulatory documents into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,   # size of each chunk
    chunk_overlap=200, # overlap to preserve context
)


def load_pdf_text(path: str) -> str:
    """
    Reads a PDF file from disk and returns its full text as a single string.

    Args:
        path: File system path to the PDF.

    Returns:
        Extracted text from the PDF.
    """
    reader = PdfReader(path)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)

    full_text = "\n".join(pages_text)
    print(f"[DEBUG] Extracted {len(full_text)} characters from {path}")
    return full_text


def build_regulatory_documents(
    pdf_paths: List[str],
    state_codes: List[str],
) -> List[Document]:
    """
    Converts a list of regulatory PDFs into LangChain Document objects.
    Each document is tagged with a 'state' metadata field (e.g., CT, NY, NJ).

    Args:
        pdf_paths: List of file paths to regulatory PDFs.
        state_codes: List of state codes corresponding to each PDF.

    Returns:
        List of Document objects ready for chunking and embedding.
    """
    docs: List[Document] = []

    for path, state in zip(pdf_paths, state_codes):
        text = load_pdf_text(path)
        docs.append(
            Document(
                page_content=text,
                metadata={"state": state}
            )
        )
    return docs


def ingest_regulatory_pdfs(
    pdf_paths: List[str],
    state_codes: List[str],
) -> None:
    """
    High-level ingestion function:
    - Loads PDFs
    - Wraps them as Documents
    - Splits into chunks
    - Stores chunks in pgvector via PGVector

    Args:
        pdf_paths: List of file paths to regulatory PDFs.
        state_codes: List of state codes corresponding to each PDF.

    Returns:
        None. Data is persisted in PostgreSQL.
    """
    # 1. Build Document objects from PDFs
    docs = build_regulatory_documents(pdf_paths, state_codes)
    print(f"[DEBUG] Loaded {len(docs)} documents")

    # 2. Split documents into smaller chunks for better retrieval
    chunks = splitter.split_documents(docs)
    print(f"[DEBUG] Created {len(chunks)} chunks")

    # 3. Add chunks to the vector store (pgvector-backed)
    vector_store.add_documents(chunks)
    print("[DEBUG] Inserted chunks into pgvector")

def get_regulation_retriever(state_code: str):
    """
    Creates and returns a retriever over the regulatory_embeddings collection.

    The retriever is used by agents to fetch relevant regulatory rules based on a natural language query (e.g., 'CT cancellation notice period').

    Returns:
        A VectorStoreRetriever object that supports .invoke(query).
    """
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5
        }
    )
