from app.rag.retriever import retrieval_service
from app.rag.formatter import format_documents
from app.rag.vectorstore import vector_store_service


def main() -> None:
    try:
        query = "What technologies did I use in SkillLink?"

        documents = retrieval_service.retrieve(query)

        context = format_documents(documents)

        print("FORMATTED CONTEXT:\n")
        print(context)

    finally:
        vector_store_service.close()


if __name__ == "__main__":
    main()