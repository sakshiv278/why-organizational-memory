from ..db import connect
from .bm25 import bm25_search
from .rbac import allowed_roles
from .reranker import rerank
from .vector_store import dense_search


def rrf(rankings: list[list[str]], k: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)


def search(query: str, role: str, top_k: int = 6, candidates: int = 12) -> list[dict]:
    """RBAC filter -> dense + BM25 -> RRF -> cross-encoder rerank -> top_k chunks."""
    roles = allowed_roles(role)
    dense = dense_search(query, roles, k=20)
    sparse = bm25_search(query, roles, k=20)
    fused = rrf([dense, sparse])[:candidates]
    if not fused:
        return []
    marks = ",".join("?" * len(fused))
    rows = {r["id"]: r for r in connect().execute(
        f"SELECT c.*, d.title, d.author FROM chunks c JOIN documents d ON d.id=c.doc_id "
        f"WHERE c.id IN ({marks}) AND c.access_role IN ({','.join('?' * len(roles))})",
        (*fused, *roles))}   # second RBAC check, defence in depth
    items = [{"chunk_id": cid, "doc_id": rows[cid]["doc_id"], "title": rows[cid]["title"],
              "author": rows[cid]["author"], "source_type": rows[cid]["source_type"],
              "timestamp": rows[cid]["timestamp"], "text": rows[cid]["text"],
              "char_start": rows[cid]["char_start"], "char_end": rows[cid]["char_end"],
              "in_dense": cid in dense, "in_bm25": cid in sparse}
             for cid in fused if cid in rows]
    return rerank(query, items)[:top_k]
