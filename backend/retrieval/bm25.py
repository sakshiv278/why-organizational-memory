import re
from ..db import connect

STOP = set("a an and are as at be by did do does for from how in is it of on or that the this to was we were what when where which who why with our us".split())


def _match_expr(query: str) -> str | None:
    terms = [t for t in re.findall(r"\w+", query.lower()) if t not in STOP]
    return " OR ".join(f'"{t}"' for t in dict.fromkeys(terms)) or None


def bm25_search(query: str, roles: list[str], k: int = 20) -> list[str]:
    expr = _match_expr(query)
    if not expr:
        return []
    marks = ",".join("?" * len(roles))
    rows = connect().execute(
        f"SELECT chunk_id FROM chunks_fts WHERE chunks_fts MATCH ? AND access_role IN ({marks}) "
        f"ORDER BY bm25(chunks_fts) LIMIT ?", (expr, *roles, k)).fetchall()
    return [r["chunk_id"] for r in rows]
