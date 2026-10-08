"""An OpenAI-compatible response whose choice has no message (Gemini blocked / empty candidate) yields an empty
LLMResponse instead of an AttributeError (the failure that killed every E3c rewrite worker on 2026-10-07)."""

import asyncio
import inspect
from types import SimpleNamespace

import vcd.llm.openai_compat as oc
from vcd.llm.base import LLMRequest


def _client(fake_create):
    cls = next(v for v in vars(oc).values() if inspect.isclass(v) and v.__module__ == oc.__name__ and hasattr(v, "complete"))
    c = cls.__new__(cls)
    c.name, c.max_tokens_param, c.supports_logprobs, c.supports_temperature = "fake", "max_tokens", False, True
    c.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create)))
    return c


def _req():
    return LLMRequest(model="m", system="s", user="u", temperature=0.3, max_tokens=50)


def test_choice_without_message_returns_empty_text():
    async def fake_create(**kwargs):
        return SimpleNamespace(choices=[SimpleNamespace(message=None, finish_reason="content_filter", logprobs=None)], usage=None, model="m")

    resp = asyncio.run(_client(fake_create).complete(_req()))
    assert resp.text == "" and resp.finish_reason == "content_filter" and resp.usage == {}


def test_no_choices_returns_empty_text():
    async def fake_create(**kwargs):
        return SimpleNamespace(choices=[], usage=SimpleNamespace(prompt_tokens=3, completion_tokens=0), model="m")

    resp = asyncio.run(_client(fake_create).complete(_req()))
    assert resp.text == "" and resp.finish_reason == "no_choices" and resp.usage == {"input_tokens": 3, "output_tokens": 0}


def test_normal_message_unchanged():
    async def fake_create(**kwargs):
        msg = SimpleNamespace(content="Answer: A\nRationale: x")
        return SimpleNamespace(choices=[SimpleNamespace(message=msg, finish_reason="stop", logprobs=None)], usage=None, model="m")

    resp = asyncio.run(_client(fake_create).complete(_req()))
    assert resp.text.startswith("Answer: A") and resp.finish_reason == "stop"
