from app.rag.chain import rag_chain
from app.rag.vectorstore import vector_store_service


def main() -> None:
    queries = [
        "What technologies were used to build SkillLink?",
        "What was my CodeVita rank?",
        "Tell me about my internship experience.",
        "What is my CGPA?",
        "Tell me about a project using MongoDB.",
    ]

    try:
        for query in queries:
            print("\n" + "=" * 70)
            print("QUESTION:", query)

            answer = rag_chain.invoke(query)

            print("\nANSWER:")
            print(answer)

    finally:
        vector_store_service.close()


if __name__ == "__main__":
    main()