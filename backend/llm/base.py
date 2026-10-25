import json, re
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def chat(self, system: str, user: str, *, fast: bool = False,
             schema: dict | None = None, max_tokens: int = 512) -> str: ...

    def json(self, system: str, user: str, *, fast: bool = False,
             schema: dict | None = None, max_tokens: int = 768) -> dict | list:
        raw = self.chat(system, user, fast=fast, schema=schema or {"type": "object"},
                        max_tokens=max_tokens)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"(\{.*\}|\[.*\])", raw, re.S)   # salvage JSON from chatter
            if not m:
                raise
            return json.loads(m.group(1))
