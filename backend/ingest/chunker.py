"""Line-aware chunker. Chunks are always exact slices of Document.text, so
text[char_start:char_end] == chunk.text holds by construction.
Chat messages and transcript turns are one line each -> never split mid-turn.
Markdown headings start a new chunk."""
import re
from ..models import Chunk, Document

MAX_CHARS = 900


def chunk_document(doc: Document, max_chars: int = MAX_CHARS, overlap_units: int = 1) -> list[Chunk]:
    text = doc.text
    units = [(m.start(), m.end()) for m in re.finditer(r"[^\n]+", text)]
    spans, cur = [], []

    def flush():
        if cur:
            span = (cur[0][0], cur[-1][1])
            if not spans or span != spans[-1]:
                spans.append(span)

    for u in units:
        heading = doc.source_type == "doc" and text[u[0]] == "#"
        if cur and ((u[1] - cur[0][0]) > max_chars or heading):
            flush()
            cur[:] = [] if heading else cur[-overlap_units:]
        cur.append(u)
    flush()
    return [Chunk(id=f"{doc.id}:{i}", doc_id=doc.id, idx=i, text=text[s:e],
                  char_start=s, char_end=e) for i, (s, e) in enumerate(spans)]
