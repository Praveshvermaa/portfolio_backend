from app.config import settings
from qdrant_client import QdrantClient, models


def main() -> None:
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    try:
        collection = client.get_collection(
            collection_name=settings.qdrant_collection
        )

        sparse_vectors = collection.config.params.sparse_vectors

        if sparse_vectors and "Sparse" in sparse_vectors:
            print("Sparse vector already exists.")
        else:
            client.create_vector_name(
                collection_name=settings.qdrant_collection,
                vector_name="Sparse",
                vector_name_config=models.SparseVectorNameConfig(
                    sparse=models.SparseVectorConfig()
                ),
            )
            print("Sparse vector configuration added.")

        # Verify the updated schema
        collection = client.get_collection(
            collection_name=settings.qdrant_collection
        )

        print("\nCollection:", settings.qdrant_collection)
        print("Dense vectors:", collection.config.params.vectors)
        print("Sparse vectors:", collection.config.params.sparse_vectors)

    finally:
        client.close()


if __name__ == "__main__":
    main()