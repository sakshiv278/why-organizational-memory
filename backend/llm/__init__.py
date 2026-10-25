from .base import LLMProvider
from .. import config


def get_llm() -> LLMProvider:
    if config.LLM_PROVIDER == "ollama":
        from .ollama import OllamaLLM
        return OllamaLLM(config.OLLAMA_URL, config.LLM_MODEL,
                         config.LLM_FAST_MODEL, config.LLM_NUM_CTX)
    raise ValueError(f"Unknown LLM_PROVIDER={config.LLM_PROVIDER} (only 'ollama' implemented)")
