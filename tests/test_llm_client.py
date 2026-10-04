import asyncio

from vcd.llm.base import LLMClient, LLMRequest, LLMResponse
from vcd.llm.cache import SqliteCache


class FakeRaw:
    name = "fake"

    def __init__(self):
        self.seen: list[LLMRequest] = []

    async def complete(self, req: LLMRequest) -> LLMResponse:
        self.seen.append(req)
        return LLMResponse(text=f"Answer: A ({req.extra_body})", model="fake-model")


def test_default_extra_body_is_applied_and_part_of_cache_key(tmp_path):
    cache = SqliteCache(tmp_path / "c.sqlite")
    raw = FakeRaw()
    plain = LLMClient(raw, cache, default_extra_body=None)
    with_thinking_off = LLMClient(raw, cache, default_extra_body={"reasoning_effort": "low"})
    req = LLMRequest(model="m", system="s", user="u", temperature=0.0, max_tokens=8)

    r1 = asyncio.run(plain.complete(req))
    r2 = asyncio.run(with_thinking_off.complete(req))
    assert raw.seen[0].extra_body is None and raw.seen[1].extra_body == {"reasoning_effort": "low"}
    assert r1.text != r2.text  # different requests, different cache entries
    assert len(cache) == 2

    # an explicit extra_body on the request wins over the client default
    req2 = LLMRequest(model="m", system="s", user="u", temperature=0.0, max_tokens=8, extra_body={"x": 1})
    asyncio.run(with_thinking_off.complete(req2))
    assert raw.seen[2].extra_body == {"x": 1}

    # second identical call is served from the cache
    r3 = asyncio.run(with_thinking_off.complete(req))
    assert r3.cached and len(raw.seen) == 3
