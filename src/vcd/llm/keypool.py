"""A RawClient that spreads requests over several API keys (= several Google Cloud projects).

Why: Google's Gemini API caps each paid Tier-1 project at 10,000 requests per model per DAY. The train-set
rewrite needs ~42k Gemini requests, so one project means four to five days. Several billed projects, one key
each, give N x 10k per day. The pool round-robins over the keys and, when a key answers with the daily-quota
error, parks that key for 24 h and retries the same request on the next one at once (the generic exponential
backoff in LLMClient would otherwise burn its six retries against a limit that resets tomorrow).
"""

from __future__ import annotations

import logging
import time
from typing import Sequence

from vcd.llm.base import LLMRequest, LLMResponse, RawClient, RetryableError

log = logging.getLogger(__name__)

_DAILY_MARKERS = ("per_day", "perday", "requests_per_model_per_day", "generaterequestsperday")


class QuotaExhaustedError(RuntimeError):
    """Every key in the pool is parked on a daily quota; the caller should stop and resume tomorrow or add keys."""


def is_daily_quota_error(err: BaseException) -> bool:
    msg = str(err).lower().replace(" ", "")
    return "429" in msg and any(m in msg for m in _DAILY_MARKERS)


class KeyPoolClient:
    def __init__(self, name: str, clients: Sequence[RawClient], park_seconds: float = 24 * 3600, clock=time.time):
        if not clients:
            raise ValueError("KeyPoolClient needs at least one client")
        self.name = name
        self.clients = list(clients)
        self.park_seconds = park_seconds
        self._clock = clock
        self._parked_until = [0.0] * len(self.clients)
        self._next = 0

    def _available(self) -> list[int]:
        now = self._clock()
        return [i for i, until in enumerate(self._parked_until) if until <= now]

    def available_keys(self) -> int:
        return len(self._available())

    async def complete(self, req: LLMRequest) -> LLMResponse:
        tried: set[int] = set()
        while True:
            avail = [i for i in self._available() if i not in tried]
            if not avail:
                raise QuotaExhaustedError(
                    f"{self.name}: all {len(self.clients)} API keys are parked on their daily request quota; "
                    "add GEMINI_API_KEY_<n> keys from more billed projects or resume after the reset"
                )
            # round-robin among the available keys
            idx = min(avail, key=lambda i: (i - self._next) % len(self.clients))
            self._next = (idx + 1) % len(self.clients)
            try:
                return await self.clients[idx].complete(req)
            except RetryableError as e:
                if not is_daily_quota_error(e):
                    raise
                self._parked_until[idx] = self._clock() + self.park_seconds
                tried.add(idx)
                log.warning("%s: key #%d hit its daily quota; parking it and switching (%d keys left)", self.name, idx + 1, len(self._available()))
