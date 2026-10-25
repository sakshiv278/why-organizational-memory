"""Safe parsers for user-uploaded organizational knowledge files."""
import csv, io, json
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Tuple

TEXT_EXTS = {'.txt', '.md', '.markdown', '.log'}


def extract_upload(filename: str, content: bytes) -> Tuple[str, str, str]:
    """Return (title, inferred source_type, normalized text)."""
    path = Path(filename or 'uploaded-file.txt')
    ext = path.suffix.lower()
    title = path.stem.replace('_', ' ').replace('-', ' ').strip() or 'Uploaded document'
    if ext == '.pdf':
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise ValueError('PDF support is not installed. Run: pip install pypdf') from e
        reader = PdfReader(io.BytesIO(content))
        pages = []
        for i, page in enumerate(reader.pages, 1):
            text = (page.extract_text() or '').strip()
            if text:
                pages.append(f'[Page {i}]\n{text}')
        text = '\n\n'.join(pages)
        if not text.strip():
            raise ValueError('No selectable text found in this PDF. Scanned PDFs need OCR before ingestion.')
        return title, 'doc', text
    if ext == '.eml':
        msg = BytesParser(policy=policy.default).parsebytes(content)
        body_parts = []
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain' and not part.get_filename():
                    body_parts.append(part.get_content())
        elif msg.get_content_type() == 'text/plain':
            body_parts.append(msg.get_content())
        headers = [f"Subject: {msg.get('subject', title)}", f"From: {msg.get('from', 'Unknown')}",
                   f"To: {msg.get('to', 'Unknown')}", f"Date: {msg.get('date', 'Unknown')}"]
        return title, 'email', '\n'.join(headers) + '\n\n' + '\n\n'.join(body_parts)
    if ext in TEXT_EXTS:
        return title, 'doc', content.decode('utf-8-sig', errors='replace')
    if ext == '.json':
        raw = json.loads(content.decode('utf-8-sig'))
        # Slack export channel files are arrays of messages; tolerate common export shapes.
        messages = raw if isinstance(raw, list) else raw.get('messages', []) if isinstance(raw, dict) else []
        if messages and all(isinstance(m, dict) for m in messages):
            lines = []
            for m in messages:
                user = m.get('user_profile', {}).get('real_name') if isinstance(m.get('user_profile'), dict) else None
                user = user or m.get('user_name') or m.get('username') or m.get('user') or 'Unknown'
                ts = m.get('ts') or m.get('timestamp') or ''
                text = m.get('text') or m.get('message') or ''
                if text:
                    lines.append(f'[{user} | {ts}] {text}')
            if lines:
                return title, 'chat', '\n'.join(lines)
        return title, 'doc', json.dumps(raw, ensure_ascii=False, indent=2)
    if ext == '.csv':
        decoded = content.decode('utf-8-sig', errors='replace')
        rows = list(csv.reader(io.StringIO(decoded)))
        return title, 'doc', '\n'.join(' | '.join(cell for cell in row) for row in rows)
    if ext == '.docx':
        try:
            from docx import Document as DocxDocument
        except ImportError as e:
            raise ValueError('DOCX support is not installed. Run: pip install python-docx') from e
        doc = DocxDocument(io.BytesIO(content))
        return title, 'doc', '\n'.join(p.text for p in doc.paragraphs if p.text.strip())
    raise ValueError(f'Unsupported file type: {ext or "(no extension)"}. Upload PDF, TXT, MD, EML, JSON, CSV, or DOCX.')
