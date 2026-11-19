from langchain_core.documents import Document


def format_documents(documents: list[Document]) -> str:
    if not documents:
        return "No relevant portfolio context was retrieved."

    formatted_chunks = []

    for document in documents:
        section = document.metadata.get("section", "Portfolio Information")

        formatted_chunk = (
            f"{section}\n"
            f"{document.page_content}"
        )

        formatted_chunks.append(formatted_chunk)

    return "\n\n".join(formatted_chunks)