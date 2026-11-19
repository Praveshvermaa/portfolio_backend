from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.llm.client import llm
from app.prompts.rag_prompt import rag_prompt
from app.rag.formatter import format_documents
from app.rag.retriever import retrieval_service


retriever = retrieval_service.get_retriever()

rag_chain = (
    {
        "context": retriever | format_documents,
        "question": RunnablePassthrough(),
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)