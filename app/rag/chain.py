from __future__ import annotations

import logging
from typing import AsyncIterator, List

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

from app.llm.client import llm
from app.prompts.rag_prompt import rag_prompt
from app.rag.retriever import get_retriever, retriever

logger = logging.getLogger(__name__)


def format_docs(docs: List[Document]) -> str:
    """
    Combines retrieved documents into a formatted markdown string.
    """
    if not docs:
        return "No specific portfolio documents matched the query."

    formatted = []
    for doc in docs:
        section = doc.metadata.get("section", "")
        content = doc.page_content.strip()
        if section and not content.startswith(section):
            formatted.append(f"{section}\n{content}")
        else:
            formatted.append(content)

    return "\n\n---\n\n".join(formatted)


# Primary LCEL RAG Chain
rag_chain = (
    RunnableParallel(
        context=retriever | format_docs,
        question=RunnablePassthrough(),
    )
    | rag_prompt
    | llm
    | StrOutputParser()
)


def run_rag_chain(question: str) -> str:
    """
    Synchronously runs the RAG chain for a given question and returns the answer.
    """
    return rag_chain.invoke(question)


async def arun_rag_chain(question: str) -> str:
    """
    Asynchronously runs the RAG chain for a given question and returns the answer.
    """
    return await rag_chain.ainvoke(question)


async def stream_rag_chain(question: str) -> AsyncIterator[str]:
    """
    Streams text chunks from the RAG chain for real-time frontend streaming.
    """
    async for chunk in rag_chain.astream(question):
        yield chunk


async def get_answer_with_sources(question: str) -> dict:
    """
    Retrieves context documents and generates an answer, returning both the response
    and metadata about source sections used.
    """
    docs = retriever.invoke(question)
    context_str = format_docs(docs)
    prompt_val = await rag_prompt.ainvoke({"context": context_str, "question": question})
    response = await llm.ainvoke(prompt_val)

    sources = list(dict.fromkeys(
        doc.metadata.get("section", "General")
        for doc in docs
        if doc.metadata.get("section")
    ))

    return {
        "question": question,
        "answer": str(response.content),
        "sources": sources,
        "context_documents": [doc.page_content for doc in docs],
    }
