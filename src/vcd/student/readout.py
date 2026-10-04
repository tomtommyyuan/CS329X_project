"""Student readout: next-token distribution after the assistant prefix "Answer:" -> TeacherResponse rows.

Protocol (docs/05_training_stack.md §5, docs/03 §8): the prompt is rendered with the SAME plain-text
template used for SFT, the unrestricted next-token softmax q is read, and the two option letters get mass
m_X = q[" X"] + q["X"] (only these two spellings exist in the training targets). p_letters is m renormalized
over {A, B}; category is "answer" iff m_A + m_B >= answer_mass_min, else "malformed". The unrestricted top-1
token is stored in `usage` so malformed outputs can be inspected. One row per prompt (one option order);
averaging over orders is done downstream by `vcd.teacher.profile.symmetrize`.

Two backends: `TransformersBackend` (forward pass, full softmax, CPU ok) and `VllmBackend` (optional
import, logprobs of a 1-token generation). Both return, per prompt, a sparse {token_id: prob} dict that
always contains the letter ids plus the top-k tokens, so `readout_rows` is a pure function of that dict.
"""

from __future__ import annotations

import datetime as _dt
import logging
import time
from typing import Iterable, Optional, Sequence

import numpy as np

from vcd.schemas import Prompt, TeacherResponse
from vcd.teacher.parse import p_x_from_letters

from vcd.train.data import ASSISTANT_PREFIX, render_prompt  # the template has ONE owner; a missing module is a hard error


log = logging.getLogger(__name__)

LETTERS: tuple[str, str] = ("A", "B")
SparseProbs = dict[int, float]


# --------------------------------------------------------------------------- token ids


def letter_token_ids(tokenizer) -> dict[str, list[int]]:
    """{'A': [id(' A'), id('A')], 'B': [id(' B'), id('B')]} with add_special_tokens=False.

    Each spelling is expected to be exactly one token (true for Qwen3 and SmolLM2). If a tokenizer splits
    a spelling, the first token id of the encoding is used and a warning is logged, because the readout
    then only lower-bounds that spelling's mass.
    """
    out: dict[str, list[int]] = {}
    for letter in LETTERS:
        ids: list[int] = []
        for spelling in (f" {letter}", letter):
            enc = tokenizer.encode(spelling, add_special_tokens=False)
            if len(enc) != 1:
                log.warning("tokenizer splits %r into %d tokens %s; using the first id only", spelling, len(enc), enc)
            if enc and enc[0] not in ids:
                ids.append(int(enc[0]))
        if not ids:
            raise ValueError(f"tokenizer produced no token for letter {letter!r}")
        out[letter] = ids
    return out


def letter_mass(probs: SparseProbs | np.ndarray, token_ids: dict[str, list[int]]) -> dict[str, float]:
    """m_X = sum of q over the spellings of X. `probs` is a sparse dict or a full-vocab vector."""
    get = (lambda i: float(probs.get(i, 0.0))) if isinstance(probs, dict) else (lambda i: float(probs[i]))
    return {letter: sum(get(i) for i in ids) for letter, ids in token_ids.items()}


def _top1(probs: SparseProbs | np.ndarray) -> tuple[int, float]:
    if isinstance(probs, dict):
        tid = max(probs, key=probs.get)
        return int(tid), float(probs[tid])
    tid = int(np.argmax(probs))
    return tid, float(probs[tid])


# --------------------------------------------------------------------------- rows


def readout_rows(
    prompts: Sequence[Prompt],
    next_token_probs: Sequence[SparseProbs] | np.ndarray,
    token_ids: dict[str, list[int]],
    tokenizer,
    run_id: str,
    model_name: str,
    backend: str,
    answer_mass_min: float = 0.9,
    n_prompt_tokens: Optional[Sequence[int]] = None,
) -> list[TeacherResponse]:
    """Pure function from next-token distributions (one per prompt) to TeacherResponse rows.

    `next_token_probs` is either an (n_prompts x vocab) array or a list of sparse {token_id: prob} dicts.
    """
    if len(prompts) != len(next_token_probs):
        raise ValueError(f"{len(prompts)} prompts but {len(next_token_probs)} distributions")
    now = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    rows: list[TeacherResponse] = []
    for k, (p, q) in enumerate(zip(prompts, next_token_probs)):
        mass = letter_mass(q, token_ids)
        z = mass["A"] + mass["B"]
        top1_id, top1_p = _top1(q)
        top1 = tokenizer.decode([top1_id])
        usage = {
            "top1": top1,
            "top1_id": top1_id,
            "top1_p": top1_p,
            "mass_AB": z,
            "backend": backend,
            "n_prompt_tokens": int(n_prompt_tokens[k]) if n_prompt_tokens is not None else None,
        }
        if z > 0:
            p_letters = {"A": mass["A"] / z, "B": mass["B"] / z}
            letter = max(p_letters, key=p_letters.get)
            choice = p.letter_to_action.get(letter)
            p_x = p_x_from_letters(p_letters, p.letter_to_action)
        else:
            p_letters, letter, choice, p_x = None, None, None, None
        rows.append(
            TeacherResponse(
                prompt_id=p.prompt_id,
                teacher=run_id,
                model=model_name,
                mode="profile",
                temperature=0.0,
                pass_idx=0,
                sample_idx=0,
                raw=ASSISTANT_PREFIX + top1,
                category="answer" if z >= answer_mass_min else "malformed",
                letter=letter,
                choice_action=choice,
                p_letters=p_letters,
                p_x=p_x,
                usage=usage,
                cached=False,
                timestamp=now,
            )
        )
    return rows


def summarize_rows(rows: Sequence[TeacherResponse], backend: str, seconds: float, top_n: int = 10) -> dict:
    """Content of eval/{split}_readout_summary.json."""
    n = len(rows)
    cats: dict[str, int] = {}
    top1: dict[str, int] = {}
    mass = []
    for r in rows:
        cats[r.category] = cats.get(r.category, 0) + 1
        t = r.usage.get("top1", "")
        top1[t] = top1.get(t, 0) + 1
        mass.append(float(r.usage.get("mass_AB", 0.0)))
    top1_hist = sorted(top1.items(), key=lambda kv: -kv[1])[:top_n]
    return {
        "n": n,
        "category_counts": cats,
        "category_rates": {k: v / n for k, v in cats.items()} if n else {},
        "mean_mass_AB": float(np.mean(mass)) if mass else None,
        "top1_histogram": [{"token": t, "count": c} for t, c in top1_hist],
        "backend": backend,
        "seconds": seconds,
    }


# --------------------------------------------------------------------------- backends


def _torch_dtype(name: str):
    import torch

    return {"bfloat16": torch.bfloat16, "bf16": torch.bfloat16, "float16": torch.float16, "fp16": torch.float16, "float32": torch.float32, "fp32": torch.float32}[name]


class TransformersBackend:
    """Forward pass with right padding; reads the logits at the last non-pad position of each prompt."""

    name = "transformers"

    def __init__(self, model_path: str, dtype: str = "bfloat16", device: Optional[str] = None, top_logprobs: int = 20):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.model_path = model_path
        self.top_logprobs = top_logprobs
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        if self.device == "cpu" and dtype in ("bfloat16", "bf16", "float16", "fp16"):
            dtype = "float32"  # CPU kernels for half precision are slow or missing; results are the same up to rounding
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        self.model = AutoModelForCausalLM.from_pretrained(model_path, dtype=_torch_dtype(dtype))
        self.model.to(self.device)
        self.model.eval()
        self.token_ids = letter_token_ids(self.tokenizer)

    def next_token_probs(self, texts: Sequence[str], batch_size: int = 32) -> tuple[list[SparseProbs], list[int]]:
        import torch

        letter_ids = sorted({i for ids in self.token_ids.values() for i in ids})
        out: list[SparseProbs] = []
        n_tokens: list[int] = []
        for start in range(0, len(texts), batch_size):
            chunk = list(texts[start : start + batch_size])
            enc = self.tokenizer(chunk, add_special_tokens=False, padding=True, return_tensors="pt").to(self.device)
            with torch.no_grad():
                logits = self.model(input_ids=enc["input_ids"], attention_mask=enc["attention_mask"]).logits
            last = enc["attention_mask"].sum(1) - 1  # right padding: index of the final real token
            probs = torch.softmax(logits[torch.arange(len(chunk)), last].float(), dim=-1).cpu()
            topv, topi = probs.topk(min(self.top_logprobs, probs.shape[-1]), dim=-1)
            for b in range(len(chunk)):
                d: SparseProbs = {int(i): float(v) for v, i in zip(topv[b], topi[b])}
                for i in letter_ids:
                    d[i] = float(probs[b, i])
                out.append(d)
                n_tokens.append(int(last[b]) + 1)
        return out, n_tokens


class VllmBackend:
    """vLLM: 1-token greedy generation with top-k logprobs; letters outside the top-k get mass 0 (a lower bound).

    `LLM(max_logprobs=...)` is raised to `top_logprobs` because vLLM rejects requests above its engine cap
    (default 20). For a trained student the letters are top-1 so the truncation is irrelevant; for the untrained
    base model mass_AB may be underestimated relative to the transformers backend, which is why the gate run
    compares the two on dev (tests/test_readout.py::test_vllm_matches_transformers_if_available).
    """

    name = "vllm"

    def __init__(self, model_path: str, dtype: str = "bfloat16", top_logprobs: int = 20, max_model_len: int = 1024, gpu_memory_utilization: float = 0.85):
        from vllm import LLM, SamplingParams  # optional dependency (extras "eval"), Linux + CUDA only

        self.model_path = model_path
        self.top_logprobs = top_logprobs
        self.llm = LLM(model=model_path, dtype=dtype, max_model_len=max_model_len, gpu_memory_utilization=gpu_memory_utilization, seed=0, max_logprobs=max(int(top_logprobs), 20))
        self.params = SamplingParams(max_tokens=1, temperature=0.0, logprobs=top_logprobs)
        self.tokenizer = self.llm.get_tokenizer()
        self.token_ids = letter_token_ids(self.tokenizer)

    def next_token_probs(self, texts: Sequence[str], batch_size: int = 32) -> tuple[list[SparseProbs], list[int]]:
        # Tokenize here with add_special_tokens=False so the ids are byte-identical to the training prompt;
        # vLLM's own string path may prepend a BOS for some tokenizers.
        ids = [self.tokenizer.encode(t, add_special_tokens=False) for t in texts]
        outputs = self.llm.generate([{"prompt_token_ids": x} for x in ids], self.params, use_tqdm=False)
        out: list[SparseProbs] = []
        n_tokens: list[int] = []
        for x, o in zip(ids, outputs):
            lp = o.outputs[0].logprobs[0] if o.outputs and o.outputs[0].logprobs else {}
            out.append({int(tid): float(np.exp(v.logprob)) for tid, v in lp.items()})
            n_tokens.append(len(x))
        return out, n_tokens


def make_backend(model_path: str, backend: str = "auto", dtype: str = "bfloat16", top_logprobs: int = 20):
    """'auto' picks vllm when importable and a GPU is present, else transformers."""
    if backend == "auto":
        try:
            import torch
            import vllm  # noqa: F401

            backend = "vllm" if torch.cuda.is_available() else "transformers"
        except ImportError:
            backend = "transformers"
    if backend == "vllm":
        return VllmBackend(model_path, dtype=dtype, top_logprobs=top_logprobs)
    if backend == "transformers":
        return TransformersBackend(model_path, dtype=dtype, top_logprobs=top_logprobs)
    raise ValueError(f"unknown backend {backend!r}")


# --------------------------------------------------------------------------- driver


class Readout:
    """Scores prompts with one backend and returns TeacherResponse rows (teacher = run_id, mode 'profile')."""

    def __init__(self, model_path: str, run_id: str, backend: str = "auto", batch_size: int = 32, dtype: str = "bfloat16", top_logprobs: int = 20, answer_mass_min: float = 0.9):
        self.model_path = model_path
        self.run_id = run_id
        self.batch_size = batch_size
        self.answer_mass_min = answer_mass_min
        self.backend = make_backend(model_path, backend=backend, dtype=dtype, top_logprobs=top_logprobs)

    @property
    def backend_name(self) -> str:
        return self.backend.name

    def score_prompts(self, prompts: Iterable[Prompt]) -> list[TeacherResponse]:
        ps = list(prompts)
        texts = [render_prompt(p.system, p.user) for p in ps]
        probs, n_tok = self.backend.next_token_probs(texts, batch_size=self.batch_size)
        return readout_rows(ps, probs, self.backend.token_ids, self.backend.tokenizer, self.run_id, self.model_path, self.backend.name, self.answer_mass_min, n_tok)


def run_readout(
    model_path: str,
    prompts: Iterable[Prompt],
    run_id: str,
    backend: str = "auto",
    batch_size: int = 32,
    dtype: str = "bfloat16",
    top_logprobs: int = 20,
    answer_mass_min: float = 0.9,
) -> tuple[list[TeacherResponse], dict]:
    """Convenience wrapper: build a Readout, score, and return (rows, summary)."""
    t0 = time.time()
    rd = Readout(model_path, run_id, backend=backend, batch_size=batch_size, dtype=dtype, top_logprobs=top_logprobs, answer_mass_min=answer_mass_min)
    rows = rd.score_prompts(prompts)
    return rows, summarize_rows(rows, rd.backend_name, time.time() - t0)
