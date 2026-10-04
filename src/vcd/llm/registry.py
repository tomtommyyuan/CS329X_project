"""Build LLMClient objects from configs/models.yaml entries."""

from __future__ import annotations

import os
from typing import Any, Optional

from vcd.llm.base import LLMClient, RawClient
from vcd.llm.cache import SqliteCache


def _api_key(spec: dict[str, Any], required: bool = False) -> Optional[str]:
    key_env = spec.get("env_key")
    val = os.environ.get(key_env) if key_env else None
    if required and not val:
        raise RuntimeError(f"{key_env} is not set: export it or put it in the project .env file")
    return val


def _base_url(spec: dict[str, Any]) -> Optional[str]:
    if spec.get("base_url"):
        return spec["base_url"]
    env = spec.get("base_url_env")
    if env:
        url = os.environ.get(env)
        if not url:
            raise RuntimeError(f"environment variable {env} is not set (vLLM endpoint for {spec.get('model')})")
        return url
    return None


def build_raw_client(name: str, spec: dict[str, Any]) -> RawClient:
    provider = spec["provider"]
    if provider == "openai":
        from vcd.llm.openai_compat import OpenAICompatClient

        return OpenAICompatClient(
            name, api_key=_api_key(spec, required=True), base_url=None,
            max_tokens_param=spec.get("max_tokens_param", "max_completion_tokens"),
            supports_temperature=spec.get("supports_temperature", True),  # GPT-5-series reasoning models reject it
        )
    if provider == "openai_compat":
        from vcd.llm.openai_compat import OpenAICompatClient

        hosted_api = "base_url" in spec  # DeepSeek-style hosted API needs a real key; self-hosted vLLM does not
        return OpenAICompatClient(
            name,
            api_key=_api_key(spec, required=hosted_api) or "EMPTY",
            base_url=_base_url(spec),
            max_tokens_param="max_tokens",
            supports_logprobs=spec.get("readout", "logprobs") == "logprobs",
        )
    if provider == "anthropic":
        from vcd.llm.anthropic_client import AnthropicClient

        return AnthropicClient(name, api_key=_api_key(spec, required=True))
    raise ValueError(f"unknown provider {provider}")


def build_client(name: str, spec: dict[str, Any], e0_cfg: dict[str, Any], use_cache: bool = True) -> LLMClient:
    cache = SqliteCache(e0_cfg["paths"]["cache"]) if use_cache else None
    concurrency = int(e0_cfg.get("concurrency", {}).get(spec["provider"], 4))
    return LLMClient(build_raw_client(name, spec), cache, concurrency=concurrency, default_extra_body=spec.get("extra_body") or None)


def teacher_spec(models_cfg: dict[str, Any], key: str) -> dict[str, Any]:
    if key in models_cfg.get("teachers", {}):
        return models_cfg["teachers"][key]
    for section in ("rewriter", "judge", "auditor", "rewriter_candidates", "judge_fallback"):
        if key in models_cfg.get(section, {}):
            return models_cfg[section][key]
    raise KeyError(f"model key {key!r} not in configs/models.yaml")
