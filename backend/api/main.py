from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from ..answer.generator import answer_question
from ..db import connect
from ..config import ROLE_ACCESS
from ..ingest.upload_service import ingest_upload

app = FastAPI(title='WHY — Organizational Memory Intelligence', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:8501'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    role: str = 'engineer'

@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'WHY'}

@app.post('/api/ask')
def ask(body: AskRequest):
    if body.role not in ROLE_ACCESS:
        raise HTTPException(status_code=400, detail=f'Unknown role. Choose from {sorted(ROLE_ACCESS)}')
    return answer_question(body.question.strip(), body.role)



@app.post('/api/upload')
async def upload_document(
    file: UploadFile = File(...),
    source_type: str = Form('auto'),
    access_role: str = Form('public'),
):
    """Upload and index PDF, email, Slack export, transcript, or text documents."""
    allowed_types = {'auto', 'doc', 'chat', 'meeting', 'github', 'email'}
    if source_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f'Unknown source type. Choose from {sorted(allowed_types)}')
    if access_role not in {'public', 'engineering', 'finance', 'exec'}:
        raise HTTPException(status_code=400, detail='Access role must be public, engineering, finance, or exec')
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail='The uploaded file is empty')
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail='Maximum upload size is 20 MB per file')
    try:
        result = ingest_upload(file.filename or 'uploaded-file.txt', content, source_type, access_role)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Could not ingest file: {exc}') from exc


@app.get('/api/sources')
def sources(role: str = 'engineer'):
    if role not in ROLE_ACCESS:
        raise HTTPException(status_code=400, detail='Unknown role')
    allowed = sorted(ROLE_ACCESS[role])
    marks = ','.join('?' for _ in allowed)
    rows = connect().execute(f'SELECT id, source_type, title, author, timestamp, url, access_role FROM documents WHERE access_role IN ({marks}) ORDER BY timestamp DESC', allowed).fetchall()
    return {'sources': [dict(r) for r in rows]}

@app.get('/api/decisions')
def decisions(role: str = 'engineer'):
    # Timeline view over source metadata. Decision extraction is a follow-on feature; do not fabricate structured records.
    if role not in ROLE_ACCESS:
        raise HTTPException(status_code=400, detail='Unknown role')
    allowed = sorted(ROLE_ACCESS[role]); marks = ','.join('?' for _ in allowed)
    rows = connect().execute(f'SELECT id, title, source_type, timestamp, author, url FROM documents WHERE access_role IN ({marks}) ORDER BY timestamp ASC', allowed).fetchall()
    return {'timeline': [dict(r) for r in rows]}
