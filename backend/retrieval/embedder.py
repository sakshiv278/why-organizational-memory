import hashlib, re
import numpy as np
from .. import config

QUERY_PREFIX = "Represent this sentence for searching relevant passages: "  # bge convention
_model = None


def _hash_embed(texts, dim=384):
    """Deterministic bag-of-words embedding. Offline fallback + tests only."""
    out = np.zeros((len(texts), dim), dtype="float32")
    for i, t in enumerate(texts):
        for w in re.findall(r"\w+", t.lower()):
            h = int(hashlib.md5(w.encode()).hexdigest(), 16)
            out[i, h % dim] += 1.0 if (h >> 20) & 1 else -1.0
    n = np.linalg.norm(out, axis=1, keepdims=True)
    return out / np.maximum(n, 1e-9)


def embed(texts: list[str], query: bool = False) -> list[list[float]]:
    global _model
    if config.EMBED_MODEL == "hash":
        return _hash_embed(texts).tolist()
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(config.EMBED_MODEL)
    if query:
        texts = [QUERY_PREFIX + t for t in texts]
    return _model.encode(texts, normalize_embeddings=True, batch_size=16).tolist()
