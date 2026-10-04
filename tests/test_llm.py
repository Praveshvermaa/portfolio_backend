from app.llm.client import llm
from app.prompts.rag_prompt import rag_prompt

messages = rag_prompt.invoke({
    "context": "RAG retrieves relevant documents before generating an answer.",
    "question": "What is RAG?"
})


response = llm.invoke(messages)

print(response.content)