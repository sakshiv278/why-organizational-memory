import math
from .. import config

_model = None


def rerank(query: str, items: list[dict]) -> list[dict]:
    """Adds item['score'] in 0..1 (sigmoid of cross-encoder logit) and sorts desc.
    RERANK_MODEL=none -> keeps fusion order, score = None (no confidence signal)."""
    global _model
    if config.RERANK_MODEL == "none" or not items:
        for it in items:
            it["score"] = None
        return items
    if _model is None:
        from sentence_transformers import CrossEncoder
        _model = CrossEncoder(config.RERANK_MODEL)
    logits = _model.predict([(query, f"{it['title']}\n{it['text']}") for it in items])
    for it, s in zip(items, logits):
        it["score"] = 1 / (1 + math.exp(-float(s)))
    return sorted(items, key=lambda x: x["score"], reverse=True)
