import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data" / "synthetic"
DB_PATH = Path(os.getenv("WHY_DB", ROOT / "data" / "why.sqlite"))
if not DB_PATH.is_absolute():
    DB_PATH = ROOT / DB_PATH

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b-instruct")
LLM_FAST_MODEL = os.getenv("LLM_FAST_MODEL", LLM_MODEL)
LLM_NUM_CTX = int(os.getenv("LLM_NUM_CTX", "4096"))

EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
RERANK_MODEL = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-base")

# Demo-grade RBAC (no auth): role -> access_role tags it may read.
ROLE_ACCESS = {
    "intern":      {"public"},
    "engineer":    {"public", "engineering"},
    "finance":     {"public", "finance"},
    "exec":        {"public", "engineering", "finance", "exec"},
}

CHROMA_PATH = Path(os.getenv("WHY_CHROMA", ROOT / "data" / "chroma"))
