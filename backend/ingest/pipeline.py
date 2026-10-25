from ..config import DATA_DIR
from ..db import init_db
from .loaders import load_corpus
from .chunker import chunk_document


def run() -> None:
    conn = init_db(reset=True)
    docs = load_corpus(DATA_DIR)
    n_chunks = 0
    for d in docs:
        conn.execute("INSERT INTO documents VALUES (?,?,?,?,?,?,?,?)",
                     (d.id, d.source_type, d.title, d.author, d.timestamp.isoformat(),
                      d.url, d.access_role, d.text))
        for c in chunk_document(d):
            conn.execute("INSERT INTO chunks VALUES (?,?,?,?,?,?,?,?,?)",
                         (c.id, c.doc_id, c.idx, c.text, c.char_start, c.char_end,
                          d.access_role, d.source_type, d.timestamp.isoformat()))
            conn.execute("INSERT INTO chunks_fts(text, chunk_id, access_role) VALUES (?,?,?)",
                         (c.text, c.id, d.access_role))
            n_chunks += 1
    conn.commit()
    print(f"ingested {len(docs)} documents, {n_chunks} chunks")


if __name__ == "__main__":
    run()
