from qdrant_client import models

from app.config import settings
from app.rag.vectorstore import vector_store_service


def main() -> None:
    try:
        client = vector_store_service.get_client()

        client.create_payload_index(
            collection_name=settings.qdrant_collection,
            field_name="metadata.section",
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )

        print("Payload index created successfully!")
        print("Field: metadata.section")
        print("Type: keyword")

    finally:
        vector_store_service.close()


if __name__ == "__main__":
    main()