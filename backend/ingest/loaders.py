import json
from datetime import datetime
from pathlib import Path
from ..models import Document


def _flatten(source_type: str, raw: str) -> str:
    """Canonical text. Chat JSON -> one '[user | ts] message' line per message."""
    if source_type == "chat":
        return "\n".join(f"[{m['user']} | {m['ts']}] {m['text']}" for m in json.loads(raw))
    return raw  # docs and meeting transcripts are already text


def load_corpus(data_dir: Path) -> list[Document]:
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    docs = []
    for m in manifest:
        raw = (data_dir / m["path"]).read_text(encoding="utf-8")
        docs.append(Document(
            id=Path(m["path"]).stem, source_type=m["source_type"], title=m["title"],
            author=m["author"], timestamp=datetime.fromisoformat(m["timestamp"]),
            url=m["url"], access_role=m["access_role"], text=_flatten(m["source_type"], raw)))
    return docs
