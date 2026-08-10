from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate

from src.vector_store import (
    load_vector_store,
    search_documents,
)


def create_llm():
    return ChatBedrockConverse(
        model_id="us.amazon.nova-2-lite-v1:0",
        region_name="us-east-1",
        credentials_profile_name="Ying",
        temperature=0,
        max_tokens=500,
    )


PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an Army AFT assistant.

Answer the user's question using only the provided context.

If the context does not contain enough information,
say that you do not have enough information.

Do not invent AFT standards or scores.

Context:
{context}
""",
        ),
        ("human", "{question}"),
    ]
)


def format_documents(documents):
    formatted = []

    for document in documents:
        source = document.metadata.get(
            "source_file",
            "unknown"
        )

        formatted.append(
            f"Source: {source}\n"
            f"{document.page_content}"
        )

    return "\n\n".join(formatted)


def ask_rag(question, k=3):
    vector_store = load_vector_store()

    documents = search_documents(
        vector_store,
        question,
        k=k,
    )

    context = format_documents(documents)

    llm = create_llm()

    chain = PROMPT | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    return {
        "answer": response.content,
        "sources": [
            document.metadata
            for document in documents
        ],
    }