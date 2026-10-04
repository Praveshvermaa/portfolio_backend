import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.rag.loader import document_loader
from app.rag.splitter import document_splitter
from app.rag.embeddings import embedding_service
from app.rag.vectorstore import get_collection_point_count, ingest_portfolio
from app.rag.retriever import retrieve_context
from app.rag.chain import run_rag_chain, stream_rag_chain, get_answer_with_sources


def test_loader_and_splitter():
    print("\n--- 1. Testing Document Loader and Splitter ---")
    doc_path = root_dir / "data" / "documents" / "portfolio.txt"
    docs = document_loader.load(doc_path)
    assert len(docs) > 0, "No documents loaded"
    print(f"[PASS] Successfully loaded {len(docs)} document from {doc_path.name}")

    chunks = document_splitter.split(docs)
    assert len(chunks) > 0, "No chunks generated"
    print(f"[PASS] Successfully split into {len(chunks)} section chunks")
    print(f"       First chunk section: {chunks[0].metadata.get('section')}")


def test_embedding_service():
    print("\n--- 2. Testing Embedding Service ---")
    query = "What is Pravesh's experience?"
    vector = embedding_service.embed_query(query)
    assert len(vector) > 0, "Embedding vector is empty"
    print(f"[PASS] Query embedded successfully. Vector dimension: {len(vector)}")


def test_vectorstore_and_retrieval():
    print("\n--- 3. Testing Qdrant Vector Store & Retrieval ---")
    count = get_collection_point_count()
    print(f"       Current Qdrant points count: {count}")
    assert count > 0, "Qdrant collection has no points"

    query = "What projects has Pravesh built?"
    docs = retrieve_context(query, k=3)
    assert len(docs) > 0, "No documents retrieved"
    print(f"[PASS] Retrieved {len(docs)} relevant chunks for query: '{query}'")
    for i, doc in enumerate(docs, 1):
        print(f"       {i}. Section: {doc.metadata.get('section', 'Unknown')}")


def test_rag_chain_invoke():
    print("\n--- 4. Testing End-to-End RAG Chain Execution ---")
    question = "What technologies does Pravesh use in his SkillLink project?"
    print(f"       Question: {question}")
    answer = run_rag_chain(question)
    assert answer and len(answer.strip()) > 0, "RAG chain returned an empty answer"
    print("\n[PASS] RAG Chain Answer:")
    print("-" * 50)
    print(answer.strip())
    print("-" * 50)


async def test_rag_streaming():
    print("\n--- 5. Testing RAG Chain Streaming Output ---")
    question = "Can Pravesh build RAG and AI applications?"
    print(f"       Question: {question}")
    print("       Streamed response: ", end="", flush=True)

    streamed_text = ""
    async for chunk in stream_rag_chain(question):
        streamed_text += chunk
        print(chunk, end="", flush=True)
    print("\n")
    assert len(streamed_text.strip()) > 0, "Streamed text was empty"
    print(f"[PASS] Successfully streamed {len(streamed_text)} characters")


async def main():
    print("========================================")
    print(" Running Full RAG Pipeline Verification ")
    print("========================================")

    test_loader_and_splitter()
    test_embedding_service()
    test_vectorstore_and_retrieval()
    test_rag_chain_invoke()
    await test_rag_streaming()

    print("\n========================================")
    print(" ALL RAG PIPELINE TESTS PASSED! ")
    print("========================================\n")


if __name__ == "__main__":
    asyncio.run(main())
