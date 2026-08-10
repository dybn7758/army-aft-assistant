from src.loader import (
    chunk_documents,
    load_documents,
)


def test_documents_load():
    documents = load_documents()

    assert len(documents) > 0


def test_document_metadata():
    documents = load_documents()

    document = documents[0]

    assert "source_file" in document.metadata
    assert "author" in document.metadata
    assert "topic" in document.metadata


def test_document_content():
    documents = load_documents()

    document = documents[0]

    assert len(document.page_content) > 0


def test_chunks_keep_metadata():
    documents = load_documents()

    chunks = chunk_documents(
        documents,
        chunk_size=200,
        chunk_overlap=50,
    )

    assert len(chunks) > 0

    for chunk in chunks:
        assert "source_file" in chunk.metadata
        assert "author" in chunk.metadata
        assert "topic" in chunk.metadata