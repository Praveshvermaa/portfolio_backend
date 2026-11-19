from collections.abc import Iterator

from app.rag.chain import rag_chain


class ChatService:
    """Handles application-level chat operations."""

    def chat(self, question: str) -> str:
        return rag_chain.invoke(question)

    def chat_stream(self, question: str) -> Iterator[str]:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        yield from rag_chain.stream(question)


chat_service = ChatService()