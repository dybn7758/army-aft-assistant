import os

from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from mem0 import MemoryClient


load_dotenv()

MEM0_API_KEY = os.getenv("MEM0_API_KEY")

if not MEM0_API_KEY:
    raise RuntimeError("MEM0_API_KEY is not configured")

mem0_client = MemoryClient(
    api_key=MEM0_API_KEY
)

session_store = {}


def get_session_history(session_id):
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()

    return session_store[session_id]


def save_long_term_memory(
    user_id,
    user_message,
    assistant_message,
):
    messages = [
        {
            "role": "user",
            "content": user_message,
        },
        {
            "role": "assistant",
            "content": assistant_message,
        },
    ]

    return mem0_client.add(
        messages=messages,
        user_id=str(user_id),
    )


def search_long_term_memory(
    user_id,
    query,
    top_k=5,
):
    return mem0_client.search(
        query=query,
        filters={
            "user_id": str(user_id)
        },
        top_k=top_k,
    )