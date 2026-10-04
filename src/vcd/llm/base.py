"""Provider-independent request/response types, caching, retry and concurrency."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
from dataclasses import asdict, dataclass, field, replace
from typing import Optional, Protocol

from vcd.llm.cache import SqliteCache

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMRequest:
    model: str
    system: str
    user: str
    temperature: float
    max_tokens: int
    logprobs: bool = False
    top_logprobs: int = 0
    seed: Optional[int] = None
    extra_body: Optional[dict] = None  # provider-specific request fields (e.g. DeepSeek thinking off); part of the cache key

    def key(self, sample_idx: int = 0) -> str:
        payload = json.dumps({**asdict(self), "sample_idx": sample_idx}, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class TokenLogprob:
    token: str
    logprob: float
    top: dict[str, float] = field(default_factory=dict)


@dataclass
class LLMResponse:
    text: str
    model: str
    finish_reason: Optional[str] = None
    token_logprobs: Optional[list[TokenLogprob]] = None
    usage: dict = field(default_factory=dict)
    cached: bool = False

    def to_json(self) -> str:
        d = asdict(self)
        d["cached"] = False
        return json.dumps(d, ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> "LLMResponse":
        d = json.loads(s)
        tl = d.get("token_logprobs")
        d["token_logprobs"] = [TokenLogprob(**t) for t in tl] if tl is not None else None
        return cls(**d)


class RawClient(Protocol):
    name: str

    async def complete(self, req: LLMRequest) -> LLMResponse: ...


class RetryableError(Exception):
    """Raised by provider clients for rate limits, 5xx and connection errors."""


class LLMClient:
    """Wraps a provider client with a sqlite cache, exponential-backoff retry and a concurrency limit."""

    def __init__(
        self,
        raw: RawClient,
        cache: Optional[SqliteCache],
        concurrency: int = 4,
        max_retries: int = 6,
        default_extra_body: Optional[dict] = None,
    ):
        self.raw = raw
        self.cache = cache
        self.sem = asyncio.Semaphore(concurrency)
        self.max_retries = max_retries
        self.default_extra_body = default_extra_body  # model-level request fields (e.g. thinking off), applied when the request has none

    async def complete(self, req: LLMRequest, sample_idx: int = 0, use_cache: bool = True) -> LLMResponse:
        if self.default_extra_body and not req.extra_body:
            req = replace(req, extra_body=dict(self.default_extra_body))
        key = f"{self.raw.name}:{req.key(sample_idx)}"
        if use_cache and self.cache is not None:
            hit = self.cache.get(key)
            if hit is not None:
                resp = LLMResponse.from_json(hit)
                resp.cached = True
                return resp
        delay = 1.0
        for attempt in range(self.max_retries + 1):
            try:
                async with self.sem:
                    resp = await self.raw.complete(req)
                break
            except RetryableError as e:
                if attempt == self.max_retries:
                    raise
                sleep = delay * (1 + random.random())
                log.warning("%s retry %d/%d after %.1fs: %s", self.raw.name, attempt + 1, self.max_retries, sleep, e)
                await asyncio.sleep(sleep)
                delay = min(delay * 2, 60)
        if self.cache is not None:
            self.cache.put(key, resp.to_json())
        return resp
