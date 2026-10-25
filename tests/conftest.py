import os, tempfile
import pytest
# Isolated, offline test environment: temp DB + temp Chroma + stub models (no downloads).
# Must be set before backend.config is imported.
_tmp = tempfile.mkdtemp(prefix="why_test_")
os.environ["EMBED_MODEL"] = "hash"
os.environ["RERANK_MODEL"] = "none"
os.environ["WHY_DB"] = os.path.join(_tmp, "why.sqlite")
os.environ["WHY_CHROMA"] = os.path.join(_tmp, "chroma")


@pytest.fixture(scope="session", autouse=True)
def corpus_and_index():
    from backend.ingest.pipeline import run
    from backend.retrieval.vector_store import build_index
    run()
    build_index()
