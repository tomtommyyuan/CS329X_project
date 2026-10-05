# Running the student grid on HAIC

Contract: `docs/05_training_stack.md` (§3 training, §7 SLURM). Cluster facts below are from the 2026-08 HAIC
notes and **must be re-checked before the first submission**: account `ingrai`, partition `hai`
(`hai-interactive` for debugging, `hai-lo` preemptible), QoS name unknown
(`sacctmgr show user $USER withassoc format=user,account%20,qos%30`; add `--qos=<name>` if a job is rejected).

## 0. One-time setup (login node)

First look at the driver: `nvidia-smi | head -4` on a compute node. On 2026-10-04 `haic-hgx-4` reported **CUDA 12.4**
(driver 550), so the torch wheel must be a **cu124** build; the latest cu124 torch is **2.6.0**. Bare `pip install torch`
(cu130) and the cu128 wheels fail with "The NVIDIA driver on your system is too old".

```bash
cd /hai/scratch/$USER && git clone https://github.com/tomtommyyuan/CS329X_project CS329X_project && cd CS329X_project
export UV_CACHE_DIR=/hai/scratch/$USER/uv-cache HF_HOME=/hai/scratch/$USER/hf

# training venv: extras first, then force the cu124 torch (the extras would otherwise pull the newest torch)
uv venv .venv --python 3.12 && source .venv/bin/activate
uv pip install -e ".[train]"
uv pip install "torch==2.6.0" --index-url https://download.pytorch.org/whl/cu124
python -c "import torch; print(torch.__version__, torch.version.cuda)"       # 2.6.0+cu124 12.4
deactivate

# eval venv: vLLM pins its own torch / transformers, so it gets a separate venv (eval.sbatch picks .venv-vllm automatically)
uv venv .venv-vllm --python 3.12
uv pip install --python .venv-vllm/bin/python "vllm==0.8.5.post1"           # built against CUDA 12.4, torch 2.6.0, supports Qwen3
uv pip install --python .venv-vllm/bin/python -e .                          # the vcd package (no extras)
.venv-vllm/bin/python -c "import torch, vllm; print(torch.__version__, torch.version.cuda, vllm.__version__)"

hf download Qwen/Qwen3-4B-Base || huggingface-cli download Qwen/Qwen3-4B-Base   # compute nodes may be offline; HF_HUB_OFFLINE=1 in jobs
hf download HuggingFaceTB/SmolLM2-135M || huggingface-cli download HuggingFaceTB/SmolLM2-135M
mkdir -p logs runs
```

If a node reports a newer driver (CUDA ≥ 12.8), the plain `uv pip install vllm` + cu128 torch route works too; the only
rule is that `torch.version.cuda` must not exceed what `nvidia-smi` shows.

Everything (repo, venvs, HF cache, runs) lives under `/hai/scratch/$USER`; the home directory is 50 GB. The head node
forbids computation, including `pytest` and `scripts/10_build_sft_data.py`: run them inside an `srun` allocation.

Both sbatch scripts take the repo root from the directory you run `sbatch` in (`SLURM_SUBMIT_DIR`), so the clone can be
named `CS329X_project` or anything else; `VENV` / `VLLM_VENV`, `HF_HOME`, `STUDENT_SHORT`, `CONFIG` can be exported to
override the defaults.

## 1. Gatekeeper: prove the stack on the cluster before the grid

```bash
# (a) unit tests + tiny CPU smoke on a compute node (never on the head node)
srun --account=ingrai -p hai-interactive --gres=gpu:h100:1 -c 8 --mem=64G -t 01:00:00 --pty bash
cd /hai/scratch/$USER/CS329X_Project && source .venv/bin/activate && export HF_HOME=/hai/scratch/$USER/hf
python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"   # must be True; cuda version <= the driver's (12.4 on haic-hgx-4)
python -m pytest -q                                                               # 39 E0 tests + train/eval tests

# (b) one REAL run with the real model but 30 steps, into a throwaway dir OUTSIDE runs/qwen3-4b/
#     (anything under runs/qwen3-4b/ that parses as {teacher}_{version}_s{seed} enters the analysis tables)
python scripts/11_train_student.py --data data/sft/gpt4o_O_s1.jsonl --out runs/_smoke/gpt4o_O_s1 --seed 1 --max-steps 30
python scripts/12_eval_student.py --run-dir runs/_smoke/gpt4o_O_s1 --split dev --limit 200 --backend transformers --out runs/_smoke/eval_tf
python scripts/12_eval_student.py --run-dir runs/_smoke/gpt4o_O_s1 --split dev --limit 200 --backend vllm --out runs/_smoke/eval_vllm
python - <<'PY'
import json; from vcd.io import read_jsonl
a = {r['prompt_id']: r['p_letters']['A'] for r in read_jsonl('runs/_smoke/eval_tf/dev_responses.jsonl') if r['p_letters']}
b = {r['prompt_id']: r['p_letters']['A'] for r in read_jsonl('runs/_smoke/eval_vllm/dev_responses.jsonl') if r['p_letters']}
d = [abs(a[k] - b[k]) for k in a if k in b]; print('vllm vs transformers: n', len(d), 'max |dP(A)|', max(d))   # must be < 1e-2
m = json.load(open('runs/_smoke/gpt4o_O_s1/train_manifest.json')); print({k: m[k] for k in ('peak_memory_gib', 'precision', 'checkpoint_dtype', 'n_dropped_too_long', 'steps_per_epoch', 'wall_time_sec')})
PY
rm -rf runs/_smoke
```

Gate checks in the smoke manifest: `n_dropped_too_long == 0`, `precision == "bf16"`, `checkpoint_dtype == "bfloat16"`,
`steps_per_epoch` ≈ n_examples / 32, **`peak_memory_gib` ≤ 70** (otherwise set `optimizer: adamw_8bit` in
configs/train.yaml, `uv pip install bitsandbytes`, and re-run the gate before the grid), and the wall time
(30 steps × 1.15 / 30 × 560 steps ≈ projected run time; the sbatch default is 2 h). The vLLM / transformers
parity on dev must hold before any test-split eval.

## 2. The 48-run core grid

3 teachers × 3 versions (O, F, C) × 5 seeds = 45, plus 3 random-label controls `random_R_s{1,2,3}`.
`train.sbatch` maps array index → (teacher, version, seed) (see its header). Only submit versions whose
SFT files exist: before the F / C rewrites are built, use the O-only list.

```bash
# full grid, at most 8 concurrent (user quota is ~8 running GPUs). Submit from the repo root with logs/ present.
# NOTE: `sbatch slurm/train.sbatch` with no args and no --array submits a job that fails inside the allocation.
sbatch --array=0-47%8 slurm/train.sbatch

# O + R only (15 + 3 runs): indices 0-4 (gpt4o O), 15-19 (claude46 O), 30-34 (deepseek_v4 O), 45-47 (R)
sbatch --array=0-4,15-19,30-34,45-47%8 slurm/train.sbatch

# one run
sbatch slurm/train.sbatch gpt4o O 1

# an arbitrary list of data files (one path per line)
ls data/sft/*_F_s*.jsonl > f_runs.txt
DATA_LIST=f_runs.txt sbatch --array=0-$(($(wc -l < f_runs.txt)-1))%8 slurm/train.sbatch

# chain the evaluation of a run on its training job
T=$(sbatch --parsable slurm/train.sbatch gpt4o O 1)
sbatch --dependency=afterok:$T slurm/eval.sbatch runs/qwen3-4b/gpt4o_O_s1 dev
sbatch --dependency=afterok:$T slurm/eval.sbatch runs/qwen3-4b/gpt4o_O_s1 test
```

Never submit the same run directory twice while a job for it is running: check
`squeue --me -o "%.9i %.4t %.60j %.12b"` and `sacct -j <id> -X --format=JobID,State,ExitCode,Elapsed,NodeList`.
Two writers to one `runs/.../checkpoint` corrupt it.

## 3. Resuming / re-running

Training saves **one** checkpoint at the end (`save_strategy: final`, 3 epochs ≈ 25–40 min on one H100), so
there is no mid-run resume: a preempted or failed run is simply re-run from scratch, and the result is
identical up to GPU nondeterminism because the data order is the file order and all seeds are fixed.

- A finished run has `runs/qwen3-4b/{teacher}_{version}_s{seed}/train_manifest.json`; `train.sbatch` and
  `11_train_student.py` skip such directories. Resubmitting `--array=0-47%8` therefore re-runs only the missing ones.
- A half-written run (log but no manifest) is overwritten by the next job; delete `checkpoint/` first if the
  node died while saving (`mv` it aside on an NFS-black-hole node, see the HAIC notes on `haic-hgx-2`).
- Find failures: `sacct -S today -X --name=vcd-train --format=JobID,JobName%20,State,ExitCode,Elapsed`; the log is
  `logs/vcd-train-<jobid>.out` (`%j`; for array tasks the per-task job id, as `squeue`/`sacct` print it).
- Disk: a bf16 checkpoint of Qwen3-4B is ~8 GB, 48 runs ≈ 0.4 TB on `/hai/scratch`. Once BOTH `eval/dev_responses.jsonl`
  and `eval/test_responses.jsonl` exist for a run, `rm -rf runs/qwen3-4b/<run>/checkpoint` (keep manifest, log, eval/).
- Do not put long runs on `hai-lo` (preemptible); if the `hai` queue is long, H200 nodes via `hai-lo` are
  acceptable for a single 40-min run that you watch.

## 4. What a run writes

```
runs/qwen3-4b/gpt4o_O_s1/
  checkpoint/              safetensors (bf16 on GPU runs) + tokenizer; vLLM loads it directly
  train_manifest.json      run_id, data sha256, n_examples, n_target_tokens, steps, peak_memory_gib, checkpoint_dtype, hyperparameters, git commit
  train_log.jsonl          {step, loss, lr, epoch, elapsed_s} every logging_steps
  eval/                    written by 12_eval_student.py
```

`run_id = "qwen3-4b.gpt4o_O_s1"` is the `teacher` field of the student's response rows (docs/05 §3.3).
