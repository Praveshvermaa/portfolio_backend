from app.rag.chain import rag_chain
from app.rag.vectorstore import vector_store_service


def main() -> None:
    question = "Tell me about the SkillLink project."

    try:
        print("Question:", question)
        print("\nAnswer: ", end="", flush=True)

        for chunk in rag_chain.stream(question):
            print(chunk, end="", flush=True)

        print("\n")

    finally:
        vector_store_service.close()


if __name__ == "__main__":
    main()