from backend.db import connect


def test_chunk_offsets_exact():
    conn = connect()
    docs = {r["id"]: r["text"] for r in conn.execute("SELECT id, text FROM documents")}
    chunks = conn.execute("SELECT * FROM chunks").fetchall()
    assert docs and chunks
    for c in chunks:
        assert docs[c["doc_id"]][c["char_start"]:c["char_end"]] == c["text"], c["id"]


def test_every_line_covered():
    conn = connect()
    for d in conn.execute("SELECT id, text FROM documents"):
        covered = [False] * len(d["text"])
        for c in conn.execute("SELECT char_start, char_end FROM chunks WHERE doc_id=?", (d["id"],)):
            for i in range(c["char_start"], c["char_end"]):
                covered[i] = True
        missing = [i for i, ch in enumerate(d["text"]) if ch != "\n" and not covered[i]]
        assert not missing, f"{d['id']} has uncovered chars"


def test_fts_role_filter():
    conn = connect()
    rows = conn.execute("SELECT chunk_id FROM chunks_fts WHERE chunks_fts MATCH 'budget' "
                        "AND access_role IN ('public')").fetchall()
    assert rows == []   # the budget doc is finance-only
