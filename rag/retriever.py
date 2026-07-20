"""
Hybrid retriever: BM25 (lexical) + sentence-embedding cosine similarity
(semantic), combined via a weighted rank fusion. This mirrors the
AstraMind Task 6 RAG design: sparse retrieval catches exact keyword
matches (tool names, certifications), dense retrieval catches paraphrased
concepts (e.g. "built REST APIs" matching a query about "backend
development experience").

Chroma is used as the vector store; BM25 runs in-memory since a resume's
chunk count is small (typically < 60 chunks).
"""
import uuid
import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

_EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# Module-level singleton: Streamlit keeps the same Python process alive
# across script reruns (it doesn't restart fresh on every click), and
# chromadb==0.4.24 has a known issue where creating a second
# chromadb.Client() instance within the same process corrupts its
# internal tenant state — "Could not connect to tenant default_tenant"
# on the second (and every subsequent) analysis run in one session.
# Creating the client once and reusing it across runs avoids this
# entirely; each run still gets its own uniquely-named collection below,
# so results from different resumes/roles never mix.
_shared_chroma_client = None


def _get_shared_client():
    global _shared_chroma_client
    if _shared_chroma_client is None:
        _shared_chroma_client = chromadb.Client()
    return _shared_chroma_client


class HybridRetriever:
    def __init__(self):
        self.embedder = SentenceTransformer(_EMBED_MODEL_NAME)
        self.client = _get_shared_client()
        collection_name = f"resume_{uuid.uuid4().hex[:8]}"
        self.collection = self.client.create_collection(name=collection_name)
        self.chunks = []
        self.bm25 = None

    def index(self, chunks: list[dict]):
        """chunks: list of {"id", "text", "section"}"""
        self.chunks = chunks
        texts = [c["text"] for c in chunks]

        # Dense: embed + store in Chroma
        embeddings = self.embedder.encode(texts, normalize_embeddings=True).tolist()
        self.collection.add(
            ids=[c["id"] for c in chunks],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{"section": c["section"]} for c in chunks],
        )

        # Sparse: tokenize for BM25
        tokenized = [t.lower().split() for t in texts]
        self.bm25 = BM25Okapi(tokenized)

    def retrieve(self, query: str, top_k: int = 5, alpha: float = 0.5) -> list[dict]:
        """
        Returns top_k chunks ranked by a fused score:
            score = alpha * normalized_semantic_score + (1 - alpha) * normalized_bm25_score
        alpha=0.5 weights lexical and semantic evenly; raise alpha to favor
        semantic matches, lower it to favor exact keyword overlap.
        """
        if not self.chunks:
            return []

        # Semantic scores via Chroma (cosine distance -> similarity)
        query_embedding = self.embedder.encode([query], normalize_embeddings=True).tolist()
        dense_results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=len(self.chunks),
        )
        dense_ids = dense_results["ids"][0]
        dense_distances = dense_results["distances"][0]
        # Chroma default distance is squared L2 on normalized vectors; convert to a similarity in [0,1]
        dense_scores = {i: 1 / (1 + d) for i, d in zip(dense_ids, dense_distances)}

        # Sparse scores via BM25
        bm25_scores_raw = self.bm25.get_scores(query.lower().split())
        max_bm25 = max(bm25_scores_raw) if max(bm25_scores_raw) > 0 else 1
        bm25_scores = {
            c["id"]: score / max_bm25
            for c, score in zip(self.chunks, bm25_scores_raw)
        }

        fused = []
        for c in self.chunks:
            cid = c["id"]
            d_score = dense_scores.get(cid, 0)
            s_score = bm25_scores.get(cid, 0)
            fused_score = alpha * d_score + (1 - alpha) * s_score
            fused.append((fused_score, c))

        fused.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in fused[:top_k]]

    def get_all_text(self) -> str:
        return "\n\n".join(c["text"] for c in self.chunks)