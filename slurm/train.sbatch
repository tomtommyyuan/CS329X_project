#!/bin/bash
# Train one student (docs/05_training_stack.md §3, §7). Three ways to call it:
#
#   sbatch slurm/train.sbatch gpt4o O 1                       # one run: (teacher, version, seed)
#   sbatch --array=0-47%8 slurm/train.sbatch                  # the 48-run core grid (index -> grid below)
#   DATA_LIST=runs.txt sbatch --array=0-$(($(wc -l < runs.txt)-1))%8 slurm/train.sbatch
#                                                             # one data file path per line, e.g. data/sft/gpt4o_F_s2.jsonl
#
# Grid index i in 0..47: i < 45 -> teacher = TEACHERS[i / 15], version = VERSIONS[(i % 15) / 5], seed = i % 5 + 1;
#                        i >= 45 -> random R, seed = i - 44.
# Each run writes runs/${STUDENT_SHORT}/${teacher}_${version}_s${seed}; a directory that already has
# train_manifest.json is skipped (safe to resubmit the array after preemption / failures).
#
# Verified 2026-10-04 (sacctmgr / scontrol): account ingrai with QoS ingrai (<= 32 GPUs per user, no --qos needed);
#   partition hai (7-day limit; gpu:h100 keeps jobs off the B200 node haic-hgx-8, which the cu124 torch cannot drive);
#   haic-hgx-2 stays excluded (NFS black hole in the 2026-08 HAIC notes, not re-tested). Re-check if a job is rejected:
#   `sacctmgr show user $USER withassoc format=user,account%20,qos%30`.
# Submit from the repo root and make sure logs/ exists (README §0): SLURM opens logs/%x-%j.out BEFORE this script
#   runs, so a missing logs/ fails the job with no log. With no arguments and no --array the job fails inside
#   the allocation (nothing is printed at submission time); always pass (teacher version seed) or --array.
#
#SBATCH --job-name=vcd-train
#SBATCH --account=ingrai
#SBATCH --partition=hai
#SBATCH --gres=gpu:h100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --exclude=haic-hgx-2
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.out
set -euo pipefail

# ---- environment: REPO defaults to the directory you ran sbatch from (the repo root); VENV overrides the venv path.
#      No module / conda on HAIC. The torch wheel must match the node driver (haic-hgx-4 reports CUDA 12.4 -> cu124 torch 2.6.0).
REPO="${REPO:-${SLURM_SUBMIT_DIR:-/hai/scratch/$USER/CS329X_Project}}"
VENV="${VENV:-$REPO/.venv}"
export HF_HOME="${HF_HOME:-/hai/scratch/$USER/hf}"
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"          # Qwen3-4B-Base must be downloaded on the login node first
export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"   # less fragmentation: fp32 master + Adam states ~60 GiB of 80
cd "$REPO"
source "$VENV/bin/activate"

STUDENT_SHORT="${STUDENT_SHORT:-qwen3-4b}"
EXTRA_ARGS="${EXTRA_ARGS:-}"                          # e.g. EXTRA_ARGS="--max-steps 30" for a gate run (word-split on purpose)
CONFIG="${CONFIG:-configs/train.yaml}"
TEACHERS=(gpt4o claude46 deepseek_v4)
VERSIONS=(O F C)

# ---- resolve (teacher, version, seed) -> data file + run dir
if [[ $# -eq 3 ]]; then
  TEACHER=$1; VERSION=$2; SEED=$3
  DATA="data/sft/${TEACHER}_${VERSION}_s${SEED}.jsonl"
elif [[ -n "${DATA_LIST:-}" ]]; then
  IDX="${SLURM_ARRAY_TASK_ID:?DATA_LIST mode needs --array}"
  DATA=$(sed -n "$((IDX + 1))p" "$DATA_LIST")
  [[ -n "$DATA" ]] || { echo "no line $((IDX + 1)) in $DATA_LIST"; exit 1; }
  NAME=$(basename "$DATA" .jsonl)                     # {teacher}_{version}_s{seed}
  [[ "$NAME" =~ ^(.+)_([OFCR])_s([0-9]+)$ ]] || { echo "cannot parse teacher/version/seed from $NAME"; exit 1; }
  TEACHER=${BASH_REMATCH[1]}; VERSION=${BASH_REMATCH[2]}; SEED=${BASH_REMATCH[3]}
else
  IDX="${SLURM_ARRAY_TASK_ID:?pass (teacher version seed) or use --array}"
  if (( IDX < 45 )); then
    TEACHER=${TEACHERS[$((IDX / 15))]}; VERSION=${VERSIONS[$(((IDX % 15) / 5))]}; SEED=$((IDX % 5 + 1))
  else
    TEACHER=random; VERSION=R; SEED=$((IDX - 44))
  fi
  DATA="data/sft/${TEACHER}_${VERSION}_s${SEED}.jsonl"
fi
RUN_DIR="runs/${STUDENT_SHORT}/${TEACHER}_${VERSION}_s${SEED}"

echo "[train.sbatch] job=${SLURM_JOB_ID:-} array=${SLURM_ARRAY_TASK_ID:-} node=$(hostname) data=$DATA run_dir=$RUN_DIR"
[[ -f "$DATA" ]] || { echo "missing $DATA (build it on the Mac with scripts/10_build_sft_data.py and rsync)"; exit 1; }
if [[ -f "$RUN_DIR/train_manifest.json" ]]; then
  echo "[train.sbatch] $RUN_DIR already finished; skipping"; exit 0
fi
python -c "import torch; assert torch.cuda.is_available(), 'no CUDA: torch wheel does not match the node driver (see slurm/README.md §0)'; print(torch.cuda.get_device_name(0))"

python scripts/11_train_student.py --data "$DATA" --out "$RUN_DIR" --seed "$SEED" --config "$CONFIG" $EXTRA_ARGS
echo "[train.sbatch] finished $RUN_DIR"
