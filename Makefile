setup:   ; pip install -r requirements.txt
corpus:  ; python data/generate_corpus.py
ingest:  ; python -m backend.ingest.pipeline
index:   ; python -m backend.retrieval.vector_store
test:    ; python -m pytest -q tests
check:   ; python scripts/check_llm.py
search:  ; python -m backend.retrieval.cli "$(Q)" --role $(or $(ROLE),engineer)
