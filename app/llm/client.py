from langchain_openai import ChatOpenAI

from app.config import settings

llm = ChatOpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.pollinations_base_url,
    model=settings.llm_model,
    temperature=0.3,
    streaming=True,
)