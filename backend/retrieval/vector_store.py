import shutil
import chromadb
from .. import config
from ..db import connect
from .embedder import embed

_client = None


def _col():
    global _client
    if _client is None:
        config.CHROMA_PATH.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(config.CHROMA_PATH))
    return _client.get_or_create_collection("why", metadata={"hnsw:space": "cosine"})


def build_index() -> int:
    """(Re)build the dense index from SQLite chunks. Title is prepended to embedded text."""
    global _client
    _client = None
    if config.CHROMA_PATH.exists():
        shutil.rmtree(config.CHROMA_PATH)
    col = _col()
    rows = connect().execute(
        "SELECT c.id, c.doc_id, c.text, c.access_role, c.source_type, d.title "
        "FROM chunks c JOIN documents d ON d.id = c.doc_id").fetchall()
    texts = [f"{r['title']}\n{r['text']}" for r in rows]
    vecs = embed(texts)
    col.add(ids=[r["id"] for r in rows], embeddings=vecs, documents=texts,
            metadatas=[{"kind": "chunk", "doc_id": r["doc_id"], "access_role": r["access_role"],
                        "source_type": r["source_type"]} for r in rows])
    return len(rows)


def dense_search(query: str, roles: list[str], k: int = 20) -> list[str]:
    res = _col().query(query_embeddings=embed([query], query=True), n_results=k,
                       where={"access_role": {"$in": roles}})
    return res["ids"][0]


if __name__ == "__main__":
    print(f"indexed {build_index()} chunks into Chroma")
