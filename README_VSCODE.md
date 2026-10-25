# WHY — run locally in VS Code

## Prerequisites
- Python 3.11 recommended
- Ollama installed and running: https://ollama.com
- VS Code with the Python extension

## 1. Open project
Extract this ZIP, then in VS Code choose **File → Open Folder** and select `why`.

## 2. Create environment and install packages
In the VS Code terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell activate with `.venv\\Scripts\\Activate.ps1`.

## 3. Download the local LLM
```bash
ollama pull qwen2.5:3b-instruct
ollama serve
```
If Ollama is already running as a background service, the second command may say the port is occupied; that is okay. Check with `ollama list`.

## 4. Build the synthetic corpus and indexes
From the project root, with the virtual environment activated:

```bash
python data/generate_corpus.py
python -m backend.ingest.pipeline
python -m backend.retrieval.vector_store
```
The default BGE embedding and reranker models may download several hundred MB the first time. For a quick offline smoke test, set `EMBED_MODEL=hash` and `RERANK_MODEL=none` in `.env` (quality will be lower). For the final demo, use the real embedding model if your machine can download it.

## 5. Start the API
Open terminal 1:

```bash
uvicorn backend.api.main:app --reload --port 8000
```
Check `http://127.0.0.1:8000/health` and interactive API docs at `http://127.0.0.1:8000/docs`.

## 6. Start the UI
Open terminal 2:

```bash
streamlit run web/app.py
```
Streamlit opens the browser. Keep the API terminal running too.

## 7. Run tests
```bash
pytest -q
```

## Important honest limitations
This is a working MVP scaffold, not a production security system. The role selector is a demo control, not authentication. Do not use confidential data. The answer generator includes retrieved excerpts and exposes citations, but citation correctness and abstention thresholds must be evaluated before claiming trustworthiness. The `/api/decisions` route currently shows a chronological source timeline; extracting and linking proposed/debated/final/reversed decision records is a next implementation step. Conflict detection, PDF/DOCX parsing, and ingestion uploads are not yet complete.
