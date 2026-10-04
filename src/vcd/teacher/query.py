"""Query a teacher on a prompt file in `demo` or `profile` mode; resumable; writes TeacherResponse rows.

demo:    T=0, full answer + rationale; one call per prompt. Logprob teachers also record p(letter).
profile: T=1, truncated to the answer line. Logprob teachers: one call, p from top_logprobs.
         Sampling teachers: k samples x passes, p = frequency (computed later in profile.py).
"""

from __future__ import annotations

import asyncio
import datetime as dt
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from tqdm.asyncio import tqdm_asyncio

from vcd.io import read_jsonl, write_jsonl
from vcd.llm.base import LLMClient, LLMRequest, LLMResponse
from vcd.schemas import Prompt, TeacherResponse
from vcd.teacher.parse import letter_probs_from_logprobs, p_x_from_letters, parse_answer

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class QueryPlan:
    teacher: str
    model: str
    mode: str  # demo | profile
    temperature: float
    max_tokens: int
    logprobs: bool
    top_logprobs: int
    k: int
    passes: int
    extra_body: Optional[dict] = None


def plan_for(teacher: str, spec: dict, e0_cfg: dict, mode: str) -> QueryPlan:
    readout = spec.get("readout", "logprobs")
    extra = spec.get("extra_body") or None
    if mode == "demo":
        return QueryPlan(
            teacher=teacher, model=spec["model"], mode="demo",
            temperature=float(e0_cfg["demo"]["temperature"]), max_tokens=int(e0_cfg["demo"]["max_tokens"]),
            logprobs=readout == "logprobs", top_logprobs=int(e0_cfg["profile"]["top_logprobs"]), k=1, passes=1,
            extra_body=extra,
        )
    if mode == "profile":
        sampling = readout == "sampling"
        return QueryPlan(
            teacher=teacher, model=spec["model"], mode="profile",
            temperature=float(e0_cfg["profile"]["temperature"]), max_tokens=int(e0_cfg["profile"]["max_tokens"]),
            logprobs=not sampling, top_logprobs=int(e0_cfg["profile"]["top_logprobs"]),
            k=int(e0_cfg["profile"]["k_sampling"]) if sampling else 1,
            passes=int(e0_cfg["profile"]["passes"]) if sampling else 1,
            extra_body=extra,
        )
    raise ValueError(mode)


def to_response(prompt: Prompt, plan: QueryPlan, resp: LLMResponse, pass_idx: int, sample_idx: int) -> TeacherResponse:
    category, letter = parse_answer(resp.text)
    choice = prompt.letter_to_action.get(letter) if letter else None
    p_letters = letter_probs_from_logprobs(resp.token_logprobs) if resp.token_logprobs else None
    p_x = p_x_from_letters(p_letters, prompt.letter_to_action) if p_letters else None
    return TeacherResponse(
        prompt_id=prompt.prompt_id, teacher=plan.teacher, model=resp.model or plan.model, mode=plan.mode,  # type: ignore[arg-type]
        temperature=plan.temperature, pass_idx=pass_idx, sample_idx=sample_idx, raw=resp.text,
        category=category, letter=letter, choice_action=choice, p_letters=p_letters, p_x=p_x,
        usage=resp.usage, cached=resp.cached, timestamp=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    )


def _done_keys(out_path: Path) -> set[tuple[str, int, int]]:
    if not out_path.exists():
        return set()
    return {(r["prompt_id"], int(r.get("pass_idx", 0)), int(r.get("sample_idx", 0))) for r in read_jsonl(out_path)}


async def run_queries(client: LLMClient, prompts: Iterable[Prompt], plan: QueryPlan, out_path: Path, use_cache: bool = True) -> dict:
    prompts = list(prompts)
    done = _done_keys(out_path)
    jobs: list[tuple[Prompt, int, int]] = [
        (p, ps, s) for p in prompts for ps in range(plan.passes) for s in range(plan.k) if (p.prompt_id, ps, s) not in done
    ]
    log.info("%s/%s: %d prompts, %d jobs to run (%d already done)", plan.teacher, plan.mode, len(prompts), len(jobs), len(done))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    usage = {"input_tokens": 0, "output_tokens": 0, "cached": 0, "calls": 0}
    lock = asyncio.Lock()

    async def one(p: Prompt, pass_idx: int, sample_idx: int) -> None:
        req = LLMRequest(
            model=plan.model, system=p.system, user=p.user, temperature=plan.temperature,
            max_tokens=plan.max_tokens, logprobs=plan.logprobs, top_logprobs=plan.top_logprobs,
            extra_body=plan.extra_body,
        )
        resp = await client.complete(req, sample_idx=pass_idx * plan.k + sample_idx, use_cache=use_cache)
        row = to_response(p, plan, resp, pass_idx, sample_idx)
        async with lock:
            write_jsonl(out_path, [row], append=True)
            usage["calls"] += 1
            usage["cached"] += int(resp.cached)
            usage["input_tokens"] += int(resp.usage.get("input_tokens", 0) or 0)
            usage["output_tokens"] += int(resp.usage.get("output_tokens", 0) or 0)

    await tqdm_asyncio.gather(*(one(p, ps, s) for p, ps, s in jobs), desc=f"{plan.teacher}:{plan.mode}")
    return usage


def estimate_cost(usage: dict, spec: dict) -> float:
    return usage["input_tokens"] / 1e6 * float(spec.get("price_in_per_m", 0)) + usage["output_tokens"] / 1e6 * float(spec.get("price_out_per_m", 0))


def summarize_file(out_path: Path) -> dict:
    cats: dict[str, int] = {}
    n = 0
    for r in read_jsonl(out_path):
        n += 1
        cats[r["category"]] = cats.get(r["category"], 0) + 1
    return {"rows": n, "categories": cats}


def main_sync(client: LLMClient, prompts: list[Prompt], plan: QueryPlan, out_path: Path, spec: dict, use_cache: bool = True) -> None:
    usage = asyncio.run(run_queries(client, prompts, plan, out_path, use_cache=use_cache))
    print(json.dumps({"usage": usage, "est_cost_usd": round(estimate_cost(usage, spec), 4), "file": summarize_file(out_path)}, indent=2))
