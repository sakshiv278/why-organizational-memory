from backend.retrieval.hybrid import rrf, search


def test_rrf_prefers_items_in_both_lists():
    assert rrf([["a", "b", "c"], ["c", "a", "d"]])[0] == "a"


def test_reversal_question_finds_reversal_sources():
    ids = {r["doc_id"] for r in search("Why did we move tracking events back to Postgres?", "engineer")}
    assert ids & {"adr-012-back-to-postgres", "2025-01-storage-review"}


def test_rbac_blocks_restricted_docs():
    q = "Q1 cloud budget cut headcount freeze"
    assert "finance-q1-budget" not in {r["doc_id"] for r in search(q, "intern")}
    assert "finance-q1-budget" not in {r["doc_id"] for r in search(q, "engineer")}
    assert "finance-q1-budget" in {r["doc_id"] for r in search(q, "finance")}


def test_exec_memo_only_for_exec():
    q = "reorg Platform Integrations merge Marcus"
    assert "exec-reorg-memo" not in {r["doc_id"] for r in search(q, "engineer")}
    assert "exec-reorg-memo" in {r["doc_id"] for r in search(q, "exec")}
