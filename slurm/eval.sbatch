#!/bin/bash
# Student readout on one run directory (docs/05_training_stack.md §4, §7). Default backend: transformers, in the training
# venv. The 2026-10-04 gate found vLLM and transformers differing by bf16 noise (max |dP(A)| 0.06 > 0.01 on 200 dev
# prompts; each is equally far from an fp32 readout), so per tasks/e1_plan.md §5 every E1 / E2 readout uses ONE
# backend: transformers (full softmax, batch-size invariant). BACKEND=vllm still works (it uses .venv-vllm).
#
#   sbatch slurm/eval.sbatch <run-dir> <split>            e.g. sbatch slurm/eval.sbatch runs/qwen3-4b/gpt4o_O_s1 test
#   sbatch --dependency=afterok:$TRAIN_JOB slurm/eval.sbatch runs/qwen3-4b/gpt4o_O_s1 test
#   MODEL=Qwen/Qwen3-4B-Base sbatch slurm/eval.sbatch - dev   # untrained base S_0 (run id {short}.base_B_s0)
#
# Submit from the repo root with logs/ present (SLURM opens the log before the script runs).
# Account / partition / exclude verified 2026-10-04 (see train.sbatch); re-check if rejected:
#   sacctmgr show user $USER withassoc format=user,account%20,qos%30
# Login node does no compute. Install once on the cluster as in README §0: vLLM lives ONLY in its own venv (.venv-vllm,
#   vllm==0.8.5.post1 on torch 2.6.0 / CUDA 12.4). Never install ".[eval]" into the training .venv: the unpinned vllm
#   pulls a torch-2.11 stack (torchvision etc.) that breaks `import transformers` next to the cu124 torch.
#   HF_HOME=/hai/scratch/$USER/hf huggingface-cli download Qwen/Qwen3-4B-Base
#
#SBATCH --job-name=vcd-eval
#SBATCH --account=ingrai
#SBATCH --partition=hai
#SBATCH --gres=gpu:h100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --exclude=haic-hgx-2
#SBATCH --output=logs/%x-%j.out

set -euo pipefail

RUN_DIR="${1:?usage: sbatch slurm/eval.sbatch <run-dir|-> <split>}"
SPLIT="${2:-test}"
PROJECT="${PROJECT:-${SLURM_SUBMIT_DIR:-/hai/scratch/$USER/CS329X_Project}}"   # defaults to the dir you ran sbatch from
BACKEND="${BACKEND:-transformers}"   # see the header: one backend for all E1 / E2 readouts
BATCH="${BATCH:-64}"

cd "$PROJECT"
REPO="$PROJECT"
# transformers backend -> the training venv (transformers 5.x, reads the checkpoints natively and honours dtype=);
# vllm backend -> .venv-vllm (vllm 0.8.5.post1 + transformers 4.51, whose from_pretrained rejects the readout's dtype=)
if [[ "$BACKEND" == "vllm" ]]; then
  VENV="${VLLM_VENV:-$REPO/.venv-vllm}"; [ -d "$VENV" ] || VENV="$REPO/.venv"
else
  VENV="${VENV:-$REPO/.venv}"
fi
source "$VENV/bin/activate"
export HF_HOME="${HF_HOME:-/hai/scratch/$USER/hf}"
export HF_HUB_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
export VLLM_LOGGING_LEVEL="${VLLM_LOGGING_LEVEL:-WARNING}"

echo "host=$(hostname) job=${SLURM_JOB_ID:-local} run_dir=$RUN_DIR split=$SPLIT backend=$BACKEND"
python -c "import torch; assert torch.cuda.is_available(), 'no GPU visible: torch wheel does not match the node driver (README §0)'; print(torch.cuda.get_device_name(0))"

if [[ "$RUN_DIR" == "-" ]]; then
  # untrained base model; MODEL defaults to the student in configs/train.yaml
  MODEL="${MODEL:-$(python -c "import yaml;print(yaml.safe_load(open('configs/train.yaml'))['student_model'])")}"
  python scripts/12_eval_student.py --model "$MODEL" --split "$SPLIT" --backend "$BACKEND" --batch-size "$BATCH" ${EXTRA_ARGS:-}
else
  if [[ ! -d "$RUN_DIR/checkpoint" ]]; then
    echo "no checkpoint under $RUN_DIR (training not finished?)" >&2
    exit 2
  fi
  if [[ -f "$RUN_DIR/eval/${SPLIT}_responses.jsonl" && -z "${OVERWRITE:-}" ]]; then
    echo "$RUN_DIR/eval/${SPLIT}_responses.jsonl exists; set OVERWRITE=1 to redo"
    exit 0
  fi
  python scripts/12_eval_student.py --run-dir "$RUN_DIR" --split "$SPLIT" --backend "$BACKEND" --batch-size "$BATCH" ${OVERWRITE:+--overwrite} ${EXTRA_ARGS:-}
fi
