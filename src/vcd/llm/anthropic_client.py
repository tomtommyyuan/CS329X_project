"""Anthropic Messages client (anthropic SDK 1.x).

Notes that matter for this project:
- `temperature` is gone from the 1.x method signature but Claude Sonnet 4.6 still accepts it on the
  wire, so it is passed through `extra_body`. Newer Claude 5.x models reject non-default values; set
  `supports_temperature=False` for those.
- `thinking` is omitted on purpose: on the 4.6 line that runs the model without extended thinking.
- No logprobs are available; choice distributions are estimated by repeated sampling (profile.py).
"""

from __future__ import annotations

from typing import Optional

import anthropic
from anthropic import AsyncAnthropic

from vcd.llm.base import LLMRequest, LLMResponse, RetryableError

_RETRY_STATUS = {408, 409, 429, 529}


class AnthropicClient:
    def __init__(self, name: str, api_key: Optional[str] = None, supports_temperature: bool = True, timeout: float = 120.0):
        self.name = name
        self.supports_temperature = supports_temperature
        kwargs = {"timeout": timeout, "max_retries": 2}
        if api_key:
            kwargs["api_key"] = api_key
        self.client = AsyncAnthropic(**kwargs)

    async def complete(self, req: LLMRequest) -> LLMResponse:
        kwargs: dict = dict(
            model=req.model,
            max_tokens=req.max_tokens,
            system=req.system,
            messages=[{"role": "user", "content": req.user}],
        )
        extra: dict = dict(req.extra_body or {})
        if self.supports_temperature:
            extra["temperature"] = req.temperature
        if extra:
            kwargs["extra_body"] = extra
        try:
            resp = await self.client.messages.create(**kwargs)
        except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.APITimeoutError, anthropic.InternalServerError) as e:
            raise RetryableError(str(e)) from e
        except anthropic.APIStatusError as e:
            if e.status_code >= 500 or e.status_code in _RETRY_STATUS:
                raise RetryableError(str(e)) from e
            raise
        text = "".join(block.text for block in resp.content if getattr(block, "type", None) == "text")
        usage = {}
        if getattr(resp, "usage", None) is not None:
            usage = {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens}
        return LLMResponse(text=text, model=getattr(resp, "model", req.model), finish_reason=getattr(resp, "stop_reason", None), token_logprobs=None, usage=usage)
