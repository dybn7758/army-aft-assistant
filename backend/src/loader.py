from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"


def parse_document(file_path):
    """
    Read a text file and extract metadata from the header.
    """

    text = file_path.read_text(encoding="utf-8")

    lines = text.splitlines()

    metadata = {
        "source_file": file_path.name,
    }

    content_lines = []
    reading_metadata = True

    for line in lines:
        stripped = line.strip()

        if reading_metadata and not stripped:
            reading_metadata = False
            continue

        if reading_metadata and ":" in line:
            key, value = line.split(":", 1)

            metadata[key.strip().lower()] = value.strip()
        else:
            reading_metadata = False
            content_lines.append(line)

    content = "\n".join(content_lines).strip()

    return Document(
        page_content=content,
        metadata=metadata,
    )


def load_documents(directory=KNOWLEDGE_BASE_DIR):
    """
    Load every .txt document from the knowledge base.
    """

    directory = Path(directory)

    documents = []

    for file_path in directory.glob("*.txt"):
        document = parse_document(file_path)
        documents.append(document)

    return documents


def chunk_documents(
    documents,
    chunk_size=500,
    chunk_overlap=100,
):
    """
    Split documents into smaller chunks.

    LangChain automatically copies Document metadata
    into the resulting chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return splitter.split_documents(documents)


def load_and_chunk_documents(
    directory=KNOWLEDGE_BASE_DIR,
    chunk_size=500,
    chunk_overlap=100,
):
    documents = load_documents(directory)

    return chunk_documents(
        documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )