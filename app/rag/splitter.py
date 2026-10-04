from __future__ import annotations

import re

from langchain_core.documents import Document


class SectionChunker:

    SECTION_PATTERN = r"(?=^\[.*\]$)"

    def split(self, documents: list[Document]) -> list[Document]:
        if not documents:
            return []

        chunks: list[Document] = []

        for document in documents:
            sections = re.split(
                self.SECTION_PATTERN,
                document.page_content,
                flags=re.MULTILINE,
            )

            for section in sections:
                section = section.strip()

                if not section:
                    continue

                header = section.split("\n", 1)[0].strip()

                chunks.append(
                    Document(
                        page_content=section,
                        metadata={
                            **document.metadata,
                            "section": header,
                        },
                    )
                )

        return chunks

    @staticmethod
    def _get_section_name(section: str) -> str:
        return section.split("\n", 1)[0].strip()

document_splitter = SectionChunker()