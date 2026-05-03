import numpy as np
import faiss
from openai import OpenAI
from app.core.config import NVIDIA_API_KEY

# Configure NVIDIA Client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

class VectorStore:
    def __init__(self):
        self.texts = []
        self.index = None
        self.dimension = None

    # 🔹 Create embedding using NVIDIA
    def _embed(self, text: str):
        # input_type is required for nv-embedqa-e5-v5
        response = client.embeddings.create(
            input=[text],
            model="nvidia/nv-embedqa-e5-v5",
            extra_body={"input_type": "query"}
        )
        return np.array(response.data[0].embedding, dtype="float32")

    # 🔹 Build FAISS index
    def build(self, chunks: list[str]):
        if not chunks:
            raise ValueError("Chunks list is empty")

        self.texts = chunks

        # Create embeddings for all chunks
        # input_type is required for nv-embedqa-e5-v5
        response = client.embeddings.create(
            input=chunks,
            model="nvidia/nv-embedqa-e5-v5",
            extra_body={"input_type": "passage"}
        )
        
        embeddings = [np.array(e.embedding, dtype="float32") for e in response.data]

        self.dimension = len(embeddings[0])

        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)

        # Convert to numpy array
        vectors = np.array(embeddings).astype("float32")

        self.index.add(vectors)

    # 🔹 Search similar chunks
    def search(self, query: str, k: int = 3):
        if self.index is None:
            raise ValueError("Index not built. Call build() first.")

        query_vector = self._embed(query).reshape(1, -1)

        distances, indices = self.index.search(query_vector, k)

        results = []
        for idx in indices[0]:
            if idx < len(self.texts):
                results.append(self.texts[idx])

        return results

    # 🔹 Simple Keyword Search
    def keyword_search(self, query: str, k: int = 2):
        if not self.texts:
            return []
            
        query_words = query.lower().split()
        scores = []
        
        for text in self.texts:
            text_lower = text.lower()
            score = 0
            for word in query_words:
                if word in text_lower:
                    score += 1
            scores.append(score)
            
        # Get indices of top k scores (excluding 0 scores)
        top_indices = np.argsort(scores)[::-1][:k]
        results = [self.texts[i] for i in top_indices if scores[i] > 0]
        return results

    # 🔹 Save index and texts to disk
    def save(self, index_path: str = "app/data/faiss_index.bin", texts_path: str = "app/data/texts.json"):
        import json
        if self.index is None:
            raise ValueError("Index not built.")
        faiss.write_index(self.index, index_path)
        with open(texts_path, "w") as f:
            json.dump(self.texts, f)

    # 🔹 Load index and texts from disk
    def load(self, index_path: str = "app/data/faiss_index.bin", texts_path: str = "app/data/texts.json"):
        import json
        self.index = faiss.read_index(index_path)
        with open(texts_path, "r") as f:
            self.texts = json.load(f)
        self.dimension = self.index.d