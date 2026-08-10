from src.vector_store import build_and_save_vector_store


def main():
    vector_store = build_and_save_vector_store()

    print("FAISS vector store created successfully.🎉")
    print(
        "Documents indexed:",
        vector_store.index.ntotal
    )


if __name__ == "__main__":
    main()
    