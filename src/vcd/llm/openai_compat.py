"""OpenAI Chat Completions client, also used for DeepSeek and vLLM (OpenAI-compatible servers)."""

from __future__ import annotations

from typing import Optional

import openai
from openai import AsyncOpenAI

from vcd.llm.base import LLMRequest, LLMResponse, RetryableError, TokenLogprob

_RETRY_STATUS = {408, 409, 429}


class OpenAICompatClient:
    def __init__(
        self,
        name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_tokens_param: str = "max_tokens",
        supports_logprobs: bool = True,
        supports_temperature: bool = True,
        timeout: float = 120.0,
    ):
        self.name = name
        self.max_tokens_param = max_tokens_param
        self.supports_logprobs = supports_logprobs
        self.supports_temperature = supports_temperature
        self.client = AsyncOpenAI(api_key=api_key or "EMPTY", base_url=base_url, timeout=timeout, max_retries=2)

    async def complete(self, req: LLMRequest) -> LLMResponse:
        kwargs: dict = dict(
            model=req.model,
            messages=[{"role": "system", "content": req.system}, {"role": "user", "content": req.user}],
        )
        kwargs[self.max_tokens_param] = req.max_tokens
        if self.supports_temperature:
            kwargs["temperature"] = req.temperature
        if req.logprobs and self.supports_logprobs:
            kwargs["logprobs"] = True
            kwargs["top_logprobs"] = max(1, min(int(req.top_logprobs or 20), 20))
        if req.seed is not None:
            kwargs["seed"] = req.seed
        if req.extra_body:
            kwargs["extra_body"] = dict(req.extra_body)
        try:
            resp = await self.client.chat.completions.create(**kwargs)
        except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError, openai.InternalServerError) as e:
            raise RetryableError(str(e)) from e
        except openai.APIStatusError as e:
            if e.status_code >= 500 or e.status_code in _RETRY_STATUS:
                raise RetryableError(str(e)) from e
            raise
        choice = resp.choices[0]
        text = choice.message.content or ""
        toks = None
        if getattr(choice, "logprobs", None) and choice.logprobs and choice.logprobs.content:
            toks = [
                TokenLogprob(
                    token=t.token,
                    logprob=float(t.logprob),
                    top={a.token: float(a.logprob) for a in (t.top_logprobs or [])},
                )
                for t in choice.logprobs.content
            ]
        usage = {}
        if resp.usage is not None:
            usage = {"input_tokens": resp.usage.prompt_tokens, "output_tokens": resp.usage.completion_tokens}
        return LLMResponse(text=text, model=resp.model or req.model, finish_reason=choice.finish_reason, token_logprobs=toks, usage=usage)

    async def first_token_logprobs(self, model: str, prompt: str, top_logprobs: int = 20) -> dict[str, float]:
        """Raw completions endpoint (vLLM / open models): next-token distribution after `prompt`.

        Used by the E0.7 readout check and by student evaluation (assistant prefix 'Answer:').
        """
        try:
            resp = await self.client.completions.create(
                model=model, prompt=prompt, max_tokens=1, temperature=0.0, logprobs=max(1, min(top_logprobs, 20))
            )
        except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError, openai.InternalServerError) as e:
            raise RetryableError(str(e)) from e
        lp = resp.choices[0].logprobs
        if lp is None or not lp.top_logprobs:
            return {}
        return {tok: float(v) for tok, v in lp.top_logprobs[0].items()}
