from app.rag.retriever import retrieval_service
from app.rag.vectorstore import vector_store_service


def main() -> None:
    queries = [
        "What technologies were used to build SkillLink?",
        "What was my CodeVita rank?",
        "Which projects did I build using React?",
        "Tell me about my internship experience.",
    ]

    try:
        for query in queries:
            results = retrieval_service.retrieve(query)

            print(f"\n{'=' * 70}")
            print("QUERY:", query)
            print("Retrieved:", len(results))

            for index, document in enumerate(results, start=1):
                print(f"\n--- Result {index} ---")
                print("Section:", document.metadata.get("section"))
                print("Content:", document.page_content)

    finally:
        vector_store_service.close()


if __name__ == "__main__":
    main()