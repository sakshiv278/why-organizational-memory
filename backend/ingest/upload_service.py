from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from ..db import init_db
from ..models import Document
from .chunker import chunk_document
from .upload_loader import extract_upload

UPLOAD_DIR = Path(__file__).resolve().parents[2] / 'data' / 'uploads'


def ingest_upload(filename: str, content: bytes, source_type: str, access_role: str) -> dict:
    title, inferred_type, text = extract_upload(filename, content)
    if not text.strip():
        raise ValueError('The uploaded file did not contain readable text.')
    # A user-selected type can override the parser's best guess.
    if source_type and source_type != 'auto':
        inferred_type = source_type
    doc_id = f'upload-{uuid4().hex[:12]}'
    safe_name = Path(filename).name
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    # Keep the original file for provenance; never use the client path.
    (UPLOAD_DIR / f'{doc_id}-{safe_name}').write_bytes(content)
    doc = Document(id=doc_id, source_type=inferred_type, title=title, author='User upload',
                   timestamp=datetime.now(timezone.utc), url='', access_role=access_role, text=text)
    conn = init_db()
    conn.execute('INSERT INTO documents VALUES (?,?,?,?,?,?,?,?)',
                 (doc.id, doc.source_type, doc.title, doc.author, doc.timestamp.isoformat(), doc.url, doc.access_role, doc.text))
    chunks = chunk_document(doc)
    for c in chunks:
        conn.execute('INSERT INTO chunks VALUES (?,?,?,?,?,?,?,?,?)',
                     (c.id, c.doc_id, c.idx, c.text, c.char_start, c.char_end, access_role, inferred_type, doc.timestamp.isoformat()))
        conn.execute('INSERT INTO chunks_fts(text, chunk_id, access_role) VALUES (?,?,?)', (c.text, c.id, access_role))
    conn.commit()
    conn.close()
    # Rebuild dense index so newly uploaded chunks become searchable immediately.
    try:
        from ..retrieval.vector_store import build_index
        indexed = build_index()
        index_message = f' Dense index now contains {indexed} chunks.'
    except Exception as exc:
        index_message = f' Keyword indexing succeeded, but dense indexing failed: {exc}'
    return {'document_id': doc_id, 'title': title, 'source_type': inferred_type,
            'access_role': access_role, 'chunks_created': len(chunks), 'characters_extracted': len(text),
            'message': f'Uploaded and indexed {title}.{index_message}'}
