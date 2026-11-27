"""Optional local embedding model, without remote API calls."""
from __future__ import annotations

class LocalEmbeddingProvider:
    """Requires sentence-transformers and pre-downloaded model weights.

    The model must emit 384-dimensional vectors. Do not silently switch models:
    reindex vectors if the model changes.
    """
    def __init__(self, model_path: str):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_path, local_files_only=True)
        if self.model.get_sentence_embedding_dimension() != 384:
            raise ValueError("Model must produce 384-dimensional embeddings")

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self.model.encode(texts, normalize_embeddings=True).tolist()
