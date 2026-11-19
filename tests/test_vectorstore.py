
from app.config import settings
from app.rag.vectorstore import vector_store_service


def main() -> None:
    try:
        vector_store = vector_store_service.connect()
        client = vector_store_service.get_client()

        collection = client.get_collection(
            collection_name=settings.qdrant_collection
        )

        print("Connection successful!")
        print("Collection:", settings.qdrant_collection)
        print("Points:", collection.points_count)
        print("Dense vector:", collection.config.params.vectors)
        print("Sparse vector:", collection.config.params.sparse_vectors)
        print("Integration:", type(vector_store).__name__)

    finally:
        vector_store_service.close()


if __name__ == "__main__":
    main()
