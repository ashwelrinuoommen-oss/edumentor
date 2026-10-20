"""
LLM Client with multi-provider abstraction supporting Claude, GPT, Gemini, Ollama, and offline Demo Mode.
"""

from edumentor.llm import LLMConfig, call_llm, call_llm_json, test_llm_connection, get_default_config

__all__ = ["LLMConfig", "call_llm", "call_llm_json", "test_llm_connection", "get_default_config"]
