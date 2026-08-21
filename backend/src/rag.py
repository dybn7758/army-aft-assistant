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

from src.models import AFTTest
from src.database import db

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

Soldier AFT test history:
{aft_history}

Computed AFT analysis:
{aft_analysis}

Use the computed AFT analysis for calculations such as latest score,
score changes, and weakest event.

Do not recalculate or contradict these values.

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

def get_user_aft_history(user_id):
    tests = (
        AFTTest.query
        .filter_by(user_id=user_id)
        .order_by(AFTTest.test_date.asc())
        .all()
    )

    if not tests:
        return "No AFT test history is available for this Soldier."

    formatted_tests = []

    for test in tests:
        formatted_tests.append(
            f"""
Test date: {test.test_date.isoformat()}
Deadlift: {test.deadlift_performance} lb, {test.deadlift_score} points
HRP: {test.hrp_performance} reps, {test.hrp_score} points
SDC: {test.sdc_performance}, {test.sdc_score} points
Plank: {test.plank_performance}, {test.plank_score} points
Two-mile run: {test.two_mile_run_performance}, {test.two_mile_run_score} points
Total score: {test.total_score}
""".strip()
        )

    return "\n\n".join(formatted_tests)

def analyze_aft_history(user_id):
    tests = (
        AFTTest.query
        .filter_by(user_id=user_id)
        .order_by(AFTTest.test_date.asc())
        .all()
    )

    if not tests:
        return {
            "summary": "No AFT test history is available.",
            "latest_score": None,
            "score_change": None,
            "weakest_event": None,
        }

    latest = tests[-1]

    event_scores = {
        "deadlift": latest.deadlift_score,
        "hrp": latest.hrp_score,
        "sdc": latest.sdc_score,
        "plank": latest.plank_score,
        "two_mile_run": latest.two_mile_run_score,
    }

    valid_scores = {
        event: score
        for event, score in event_scores.items()
        if score is not None
    }

    weakest_event = (
        min(valid_scores, key=valid_scores.get)
        if valid_scores
        else None
    )

    score_change = None

    if len(tests) >= 2:
        previous = tests[-2]

        if (
            previous.total_score is not None
            and latest.total_score is not None
        ):
            score_change = (
                latest.total_score
                - previous.total_score
            )

    return {
        "latest_score": latest.total_score,
        "latest_test_date": latest.test_date.isoformat(),
        "score_change": score_change,
        "weakest_event": weakest_event,
        "weakest_event_score": (
            valid_scores.get(weakest_event)
            if weakest_event
            else None
        ),
    }

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

    aft_history = get_user_aft_history(user_id)
    aft_analysis = analyze_aft_history(user_id)

    llm = create_llm()

    chain = PROMPT | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
            "history": session_history.messages,
            "memories": memories,
            "aft_history": aft_history,
            "aft_analysis": aft_analysis,
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