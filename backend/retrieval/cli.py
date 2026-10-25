import argparse
from .hybrid import search

ap = argparse.ArgumentParser()
ap.add_argument("query")
ap.add_argument("--role", default="engineer")
ap.add_argument("-k", type=int, default=5)
a = ap.parse_args()
for i, r in enumerate(search(a.query, a.role, top_k=a.k), 1):
    s = "n/a" if r["score"] is None else f"{r['score']:.3f}"
    src = ("D" if r["in_dense"] else "-") + ("B" if r["in_bm25"] else "-")
    print(f"{i}. score={s} [{src}] {r['doc_id']}:{r['chunk_id'].split(':')[1]}  {r['title']}")
    print("   " + r["text"][:140].replace("\n", " ") + "...")
