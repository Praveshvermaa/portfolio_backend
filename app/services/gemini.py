from openai import OpenAI
from app.core.config import NVIDIA_API_KEY

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = NVIDIA_API_KEY
)

def generate_answer(context, query):
    prompt = f"""
You are Pravesh's AI portfolio assistant.

STRICT RULES:
- Answer ONLY based on the provided context.
- If the user asks something unrelated to Pravesh's portfolio, politely say: 'I can only answer questions regarding Pravesh's professional experience and projects.'
- Do NOT make assumptions.
- Be professional and clear.

CONTEXT:
{context}

QUESTION:
{query}
"""

    completion = client.chat.completions.create(
      model="meta/llama-3.1-8b-instruct",
      messages=[{"role":"user","content":prompt}],
      temperature=0.2,
      top_p=0.7,
      max_tokens=1024,
      stream=True
    )
    
    for chunk in completion:
        if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content



