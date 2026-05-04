import os
from app.services.embed import VectorStore
from app.services.gemini import generate_answer


vector_store = VectorStore()


def chunk_text(text:str):
    # Split by double newline to keep logical sections/paragraphs intact
    raw_chunks = text.split("\n\n")
    
    chunks = []
    for chunk in raw_chunks:
        cleaned_chunk = chunk.strip()
        if len(cleaned_chunk) > 10:  # Ignore empty or very short chunks
            chunks.append(cleaned_chunk)
            
    return chunks


def load_data():
    index_path = "app/data/faiss_index.bin"
    texts_path = "app/data/texts.json"

    if os.path.exists(index_path) and os.path.exists(texts_path):
        print("Loading vector store from disk...")
        vector_store.load(index_path, texts_path)
    else:
        print("Building vector store from scratch...")
        with open("app/data/portfolio.txt", "r") as f: 
            text = f.read()

        chunks = chunk_text(text)
        vector_store.build(chunks)
        vector_store.save(index_path, texts_path)

async def ask(query): 
    # 1. Vector Search (Semantic)
    vector_results = vector_store.search(query, k=3) 
    
    # 2. Keyword Search (Exact Match)
    keyword_results = vector_store.keyword_search(query, k=2)
    
    # 3. Combine and Deduplicate
    # Keyword results are prioritized by being placed first
    combined_results = keyword_results + vector_results
    
    # Deduplicate while preserving order
    seen = set()
    context_chunks = []
    for chunk in combined_results:
        if chunk not in seen:
            context_chunks.append(chunk)
            seen.add(chunk)

    context = "\n\n".join(context_chunks) 

    # Since generate_answer is an async generator, calling it returns the generator
    return generate_answer(context, query) 
