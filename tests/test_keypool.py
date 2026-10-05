import asyncio

import pytest

from vcd.llm.base import LLMRequest, LLMResponse, RetryableError
from vcd.llm.keypool import KeyPoolClient, QuotaExhaustedError, is_daily_quota_error

DAILY = "Error code: 429 - [{'error': {'message': 'Quota exceeded for metric: generativelanguage.googleapis.com/generate_requests_per_model_per_day, limit: 10000'}}]"
MINUTE = "Error code: 429 - [{'error': {'message': 'Quota exceeded for metric: generate_content_free_tier_requests, limit: 5'}}]"


class Fake:
    def __init__(self, name, fail_daily=False):
        self.name, self.fail_daily, self.calls = name, fail_daily, 0

    async def complete(self, req):
        self.calls += 1
        if self.fail_daily:
            raise RetryableError(DAILY)
        return LLMResponse(text=f"ok from {self.name}", model=req.model)


REQ = LLMRequest(model="m", system="s", user="u", temperature=0.0, max_tokens=5)


def test_daily_quota_detection():
    assert is_daily_quota_error(RetryableError(DAILY))
    assert not is_daily_quota_error(RetryableError(MINUTE))
    assert not is_daily_quota_error(RetryableError("Error code: 500 - server error"))


def test_round_robin_and_failover():
    a, b, c = Fake("a"), Fake("b", fail_daily=True), Fake("c")
    pool = KeyPoolClient("gem", [a, b, c])
    outs = [asyncio.run(pool.complete(REQ)).text for _ in range(4)]
    assert outs == ["ok from a", "ok from c", "ok from a", "ok from c"]  # b parked after its first daily-quota error
    assert b.calls == 1 and pool.available_keys() == 2


def test_all_parked_raises_quota_exhausted():
    pool = KeyPoolClient("gem", [Fake("a", fail_daily=True), Fake("b", fail_daily=True)])
    with pytest.raises(QuotaExhaustedError):
        asyncio.run(pool.complete(REQ))


def test_minute_limit_is_left_to_the_generic_retry():
    class MinuteFail(Fake):
        async def complete(self, req):
            raise RetryableError(MINUTE)

    pool = KeyPoolClient("gem", [MinuteFail("a"), Fake("b")])
    with pytest.raises(RetryableError):
        asyncio.run(pool.complete(REQ))


def test_parked_key_returns_after_reset():
    now = [0.0]
    a = Fake("a", fail_daily=True); b = Fake("b")
    pool = KeyPoolClient("gem", [a, b], park_seconds=100, clock=lambda: now[0])
    assert asyncio.run(pool.complete(REQ)).text == "ok from b"
    a.fail_daily = False
    now[0] = 50
    assert pool.available_keys() == 1
    now[0] = 101
    assert pool.available_keys() == 2
