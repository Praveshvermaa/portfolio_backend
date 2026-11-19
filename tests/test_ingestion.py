
from app.config import settings
from app.rag.loader import document_loader
from app.rag.splitter import document_splitter
from app.rag.ingestion import ingestion_service
from app.rag.vectorstore import vector_store_service


def main() -> None:
    try:
        documents = document_loader.load(
            "data/documents/portfolio.txt"
        )

        chunks = document_splitter.split(documents)

        print("Loaded documents:", len(documents))
        print("Generated chunks:", len(chunks))
        print(chunks[0])

        ids = ingestion_service.ingest(chunks)

        print("Inserted points:", len(ids))

        client = vector_store_service.get_client()
        collection = client.get_collection(
            collection_name=settings.qdrant_collection
        )

        print("Qdrant point count:", collection.points_count)

    finally:
        vector_store_service.close()


if __name__ == "__main__":
    main()
