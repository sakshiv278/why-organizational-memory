import sqlite3
from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents(
  id TEXT PRIMARY KEY, source_type TEXT, title TEXT, author TEXT,
  timestamp TEXT, url TEXT, access_role TEXT, text TEXT);
CREATE TABLE IF NOT EXISTS chunks(
  id TEXT PRIMARY KEY, doc_id TEXT, idx INTEGER, text TEXT,
  char_start INTEGER, char_end INTEGER,
  access_role TEXT, source_type TEXT, timestamp TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
  text, chunk_id UNINDEXED, access_role UNINDEXED);
CREATE TABLE IF NOT EXISTS decisions(
  id TEXT PRIMARY KEY, decision TEXT, topic TEXT, alternatives TEXT,
  rationale TEXT, participants TEXT, date TEXT, status TEXT,
  supersedes_id TEXT, access_role TEXT, extraction_confidence REAL);
CREATE TABLE IF NOT EXISTS decision_evidence(
  decision_id TEXT, doc_id TEXT, quote TEXT, char_start INTEGER, char_end INTEGER);
CREATE TABLE IF NOT EXISTS conflicts(
  id INTEGER PRIMARY KEY AUTOINCREMENT, doc_a TEXT, quote_a TEXT,
  doc_b TEXT, quote_b TEXT, explanation TEXT);
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset: bool = False) -> sqlite3.Connection:
    if reset and DB_PATH.exists():
        DB_PATH.unlink()
    conn = connect()
    conn.executescript(SCHEMA)
    return conn
