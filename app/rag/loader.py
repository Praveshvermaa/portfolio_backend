from __future__ import annotations

from langchain_community.document_loaders import TextLoader

from langchain_core.documents import Document

from pathlib import Path

class DocumentLoader:

    SUPPORTED_EXTENSIONS = {".txt",".pdf"}

    def load(self, file_path: str | Path) -> list[Document]:

        path = Path(file_path)

        self._validate(path)

        loader = TextLoader(str(path), encoding="utf-8")

        documents = loader.load()

        if not documents:
            raise ValueError(
                f"Document returned no content: {path}"
            )

        return documents


    def _validate(self, path:Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {path.suffix}. "
                f"Supported types: {self.SUPPORTED_EXTENSIONS}"
            )

        if path.stat().st_size == 0:
            raise ValueError(
                f"Document is empty: {path}"
            )


document_loader = DocumentLoader()

        


