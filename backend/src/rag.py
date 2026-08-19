from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate

from src.vector_store import (
    load_vector_store,
    search_documents,
)

from src.memory import (
    get_session_history,
    save_long_term_memory,
    search_long_term_memory,
)

VECTOR_STORE = load_vector_store()

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

Use the provided AFT context for factual Army AFT information.

Use long-term user memories only for personalization,
such as goals or preferences.

Use conversation history to understand follow-up questions.

Do not invent AFT standards or scores.

If the AFT context does not contain enough information,
say that you do not have enough information.

Relevant user memories:
{memories}

AFT context:
{context}

Conversation history:
{history}
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


def ask_rag(
    question,
    user_id,
    session_id,
    k=3,
):
    vector_store = load_vector_store()

    documents = search_documents(
        VECTOR_STORE,
        question,
        k=k,
    )

    context = format_documents(documents)

    session_history = get_session_history(session_id)

    memory_response = search_long_term_memory(
        user_id=user_id,
        query=question,
    )

    memories = memory_response.get(
        "results",
        memory_response,
    )

    llm = create_llm()

    chain = PROMPT | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
            "history": session_history.messages,
            "memories": memories,
        }
    )

    session_history.add_user_message(question)
    session_history.add_ai_message(response.content)

    save_long_term_memory(
        user_id=user_id,
        user_message=question,
        assistant_message=response.content,
    )

    return {
        "answer": response.content,
        "sources": [
            document.metadata
            for document in documents
        ],
    }