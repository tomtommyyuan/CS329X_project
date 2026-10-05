# E1 dev diagnostics (2026-10-04, HPC side)

One-off checks behind the E1 decision in `tasks/hpc_log.md`; none of them is a pre-registered rule. Scripts in `scripts/`
(run from the repo root with `.venv/bin/python`).

| file | what |
|---|---|
| `train_label_reproduction.txt` | seed-1 students read out (transformers) on their exact training prompts (5,948 = union of the three O files): share of each teacher's training labels reproduced, and the side taken on items where two teachers' labels differ |
| `dev_calibration_contested.txt` | dev: how extreme each teacher's / student group's p_sym is; seed-pooled side-taking on contested cells (two teachers' majority acts differ) with family-bootstrap 95% CI |
| `dev_suggestibility_base_profile.txt` | dev: framing effects δ(T1..T6) and δ(T5) − δ(T6) per teacher / student group; the untrained base S_0 with the 0.9 mass rule **relaxed** (diagnostic only); seed-pooled profile correlations |
