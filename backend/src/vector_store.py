from pathlib import Path

from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import FAISS

from src.loader import load_and_chunk_documents
import os


BASE_DIR = Path(__file__).parent.parent
VECTOR_STORE_DIR = BASE_DIR / "vector_store" / "aft_index"


def create_embeddings():
    return BedrockEmbeddings(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id="amazon.titan-embed-text-v2:0",
    )


def build_vector_store():
    """
    Load AFT documents, chunk them, generate embeddings,
    and create a FAISS vector store.
    """
    chunks = load_and_chunk_documents()

    embeddings = create_embeddings()

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    return vector_store


def save_vector_store(vector_store):
    """
    Save the FAISS index locally.
    """
    VECTOR_STORE_DIR.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    vector_store.save_local(
        str(VECTOR_STORE_DIR)
    )


def build_and_save_vector_store():
    vector_store = build_vector_store()

    save_vector_store(vector_store)

    return vector_store


def search_documents(vector_store, query, k=3):
    """
    Search the FAISS vector store for document chunks
    that are semantically similar to the user's query.
    """
    return vector_store.similarity_search(
        query,
        k=k,
    )

def load_vector_store():
    embeddings = create_embeddings()

    return FAISS.load_local(
        str(VECTOR_STORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )