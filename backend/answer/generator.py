from ..llm import get_llm
from ..retrieval.hybrid import search
from ..db import connect

SYSTEM = '''You are WHY, an organizational memory assistant. Answer ONLY using supplied evidence.
Rules: cite evidence inline as [S1], [S2] etc. Do not invent facts, dates, people, or reasons.
Distinguish confirmed decisions from proposals and debates. If evidence is insufficient or conflicting, say so explicitly. If sources disagree, describe the conflict instead of choosing silently. Be concise and factual.'''

def answer_question(question: str, role: str = 'engineer') -> dict:
    hits = search(question, role, top_k=6)
    # Conservative evidence gate: do not ask the model to answer without any retrieval hits.
    if not hits:
        return {'answer': "I don't know based on the available, authorized sources. Try a more specific question or add relevant documents.", 'sources': [], 'insufficient_evidence': True}
    sources = []
    blocks = []
    for i, h in enumerate(hits, 1):
        sid = f'S{i}'
        sources.append({'id': sid, 'document_id': h['doc_id'], 'title': h['title'], 'source_type': h['source_type'], 'timestamp': h['timestamp'], 'excerpt': h['text'], 'url': _url(h['doc_id'])})
        blocks.append(f'[{sid}] title={h["title"]}; date={h["timestamp"]}; type={h["source_type"]}\n{h["text"]}')
    prompt = f'Question: {question}\n\nEvidence snippets:\n' + '\n\n'.join(blocks)
    try:
        text = get_llm().chat(SYSTEM, prompt, max_tokens=700)
    except Exception as e:
        text = 'I could not generate an answer because the local language model is unavailable. Check that Ollama is running and the configured model is installed.'
    # Return the evidence regardless; citations are generated from stable source IDs.
    return {'answer': text, 'sources': sources, 'insufficient_evidence': False}

def _url(doc_id: str) -> str | None:
    row = connect().execute('SELECT url FROM documents WHERE id=?', (doc_id,)).fetchone()
    return row['url'] if row and row['url'] else None
