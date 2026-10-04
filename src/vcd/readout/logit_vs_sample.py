"""E0.7: on an open model served by vLLM, compare the first-token logit readout after the assistant
prefix 'Answer:' with the letter frequency from k sampled generations.

The logit readout uses vLLM's `continue_final_message` so the chat template is applied by the server.
"""

from __future__ import annotations

import asyncio
from typing import Optional

import numpy as np
import pandas as pd

from vcd.llm.base import LLMRequest, TokenLogprob
from vcd.llm.openai_compat import OpenAICompatClient
from vcd.schemas import Prompt
from vcd.stats import pearson
from vcd.teacher.parse import letter_probs_from_logprobs, parse_answer


async def logit_readout(raw: OpenAICompatClient, model: str, p: Prompt, top_logprobs: int = 20) -> Optional[dict[str, float]]:
    resp = await raw.client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": p.system}, {"role": "user", "content": p.user}, {"role": "assistant", "content": "Answer:"}],
        max_tokens=1, temperature=0.0, logprobs=True, top_logprobs=top_logprobs,
        extra_body={"continue_final_message": True, "add_generation_prompt": False},
    )
    ch = resp.choices[0]
    if not ch.logprobs or not ch.logprobs.content:
        return None
    t = ch.logprobs.content[0]
    tok = TokenLogprob(token=t.token, logprob=float(t.logprob), top={a.token: float(a.logprob) for a in (t.top_logprobs or [])})
    return letter_probs_from_logprobs([TokenLogprob("Answer", 0.0, {}), tok])


async def sample_readout(client, model: str, p: Prompt, k: int, temperature: float, max_tokens: int = 8) -> dict:
    req = LLMRequest(model=model, system=p.system, user=p.user, temperature=temperature, max_tokens=max_tokens)
    outs = await asyncio.gather(*(client.complete(req, sample_idx=i) for i in range(k)))
    letters = [parse_answer(o.text)[1] for o in outs]
    n_ans = sum(l is not None for l in letters)
    return {"n_answer": n_ans, "freq_A": (sum(l == "A" for l in letters) / n_ans) if n_ans else np.nan}


async def run(client, model: str, prompts: list[Prompt], k: int, temperature: float) -> pd.DataFrame:
    raw: OpenAICompatClient = client.raw  # type: ignore[assignment]

    async def one(p: Prompt) -> dict:
        lp = await logit_readout(raw, model, p)
        sm = await sample_readout(client, model, p, k, temperature)
        return {"prompt_id": p.prompt_id, "variant": p.variant, "order": p.order, "p_logit_A": lp["A"] if lp else np.nan, **sm}

    rows = await asyncio.gather(*(one(p) for p in prompts))
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> dict:
    d = df.dropna(subset=["p_logit_A", "freq_A"])
    r, _ = pearson(d["p_logit_A"], d["freq_A"])
    return {
        "n": int(len(d)),
        "mean_abs_diff": float((d["p_logit_A"] - d["freq_A"]).abs().mean()) if len(d) else float("nan"),
        "pearson": r,
        "share_no_logit": float(df["p_logit_A"].isna().mean()) if len(df) else float("nan"),
    }
