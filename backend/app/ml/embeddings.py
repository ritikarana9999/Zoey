"""
Product embeddings for similarity-based recommendations.
Uses TF-IDF as a lightweight alternative to neural embeddings.
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


class ProductEmbedder:
    """
    Creates product embeddings from text descriptions for similarity search.
    Falls back to TF-IDF if sentence-transformers not available.
    """

    def __init__(self, use_transformers: bool = False):
        self.use_transformers = use_transformers
        self.vectorizer = None
        self.model = None
        self.embeddings = None
        self.product_ids: List[str] = []

    def _build_text(self, product: Dict) -> str:
        """Combine product fields into a single text representation."""
        parts = [
            product.get("name", ""),
            product.get("brand", "") or "",
            product.get("category_name", "") or "",
            product.get("weight_volume", "") or "",
            product.get("description", "") or "",
        ]
        return " ".join(p for p in parts if p).lower()

    def fit(self, products: List[Dict]):
        """Build embeddings for a list of products."""
        texts = [self._build_text(p) for p in products]
        self.product_ids = [str(p.get("id", i)) for i, p in enumerate(products)]

        if self.use_transformers:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                self.embeddings = self.model.encode(texts, show_progress_bar=False)
                logger.info("Using SentenceTransformer embeddings")
                return
            except ImportError:
                logger.warning("sentence-transformers not available, falling back to TF-IDF")

        # TF-IDF fallback
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            min_df=1,
        )
        self.embeddings = self.vectorizer.fit_transform(texts).toarray()
        logger.info(f"TF-IDF embeddings built for {len(products)} products")

    def find_similar(self, product_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find the most similar products to the given product ID."""
        if self.embeddings is None:
            raise RuntimeError("Must call fit() before find_similar()")

        if product_id not in self.product_ids:
            return []

        idx = self.product_ids.index(product_id)
        query_embedding = self.embeddings[idx:idx+1]

        if hasattr(self.embeddings, "toarray"):
            scores = cosine_similarity(query_embedding, self.embeddings)[0]
        else:
            scores = cosine_similarity(query_embedding, self.embeddings)[0]

        # Exclude self
        scores[idx] = -1

        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(self.product_ids[i], float(scores[i])) for i in top_indices if scores[i] > 0]

    def get_embedding(self, product_id: str) -> Optional[np.ndarray]:
        """Get the embedding vector for a product."""
        if product_id not in self.product_ids:
            return None
        idx = self.product_ids.index(product_id)
        return self.embeddings[idx]
