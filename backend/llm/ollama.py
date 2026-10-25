import requests
from .base import LLMProvider


class OllamaLLM(LLMProvider):
    def __init__(self, url, model, fast_model, num_ctx=4096, timeout=600):
        self.url, self.model, self.fast_model = url.rstrip("/"), model, fast_model
        self.num_ctx, self.timeout = num_ctx, timeout

    def chat(self, system, user, *, fast=False, schema=None, max_tokens=512):
        body = {
            "model": self.fast_model if fast else self.model,
            "stream": False,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "options": {"temperature": 0, "num_ctx": self.num_ctx,
                        "num_predict": max_tokens},
        }
        if schema is not None:
            body["format"] = schema      # Ollama constrains output to this JSON schema
        r = requests.post(f"{self.url}/api/chat", json=body, timeout=self.timeout)
        r.raise_for_status()
        return r.json()["message"]["content"]
