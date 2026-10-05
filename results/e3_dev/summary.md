# E3 summary (dev, student qwen3-4b-paired, variants T1, T3, T5, T6; E3 rule pre-specified 2026-10-05 (docs/03 E3 row, tasks/e3_plan.md §3) before any F / C run existed; not yet frozen (freeze line pending in tasks/hpc_log.md); auto-generated)

Rule (docs/03 E3 row, verbatim): 效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致；R 有而 F / C 无则归因于隐性内容变化. Operationalised (tasks/e3_plan.md §3): per metric, the per-teacher statistic is the seed mean of the paired difference S_{T,V,s} - S_{T,O,s} (disagreement: the mean V-W disagreement minus the teacher's own O-O seed-pair mean); the seed-pair null is the same single-pair quantity between two O seeds of the same teacher, pooled over teachers, and scaled to the statistic: SD_stat = sqrt(mean(d^2) / n_seeds [+ jackknife var of the O-O mean]), q95 = t(0.975, df = sum(n_O - 1) = None) x SD_stat (disagreement: t(0.95)); a teacher exceeds when |stat| > q95; effect iff >= 2/3 of the 3 teachers exceed with the same sign. p from the t reference with Holm over the teachers; `no effect` only when >= 2/3 teachers pass the TOST (family-bootstrap 95% CI inside +/- 1 SD_stat; docs/04 §3), otherwise `inconclusive`. The raw single-pair q95 (`null_q95_single`, `n_pass_single`) is a sensitivity column. Primary rows: disagreement F vs C, consistency change, excess drift, inheritance by form; the other rows are secondary. Under H0 the q95 rule has a per-row false-positive rate of about 0.004, <= 0.05 family-wise over the 13 rows (Bonferroni); `p_row_holm_primary` is descriptive. CIs are family-bootstrap 2.5 / 97.5 percentiles with families resampled jointly for every seed of a teacher. Assumptions: seed noise approximately normal and independent across seeds (same-seed F / O pairs share init and data order, so the null is conservative).

**dev = freeze split**: the verdicts below are descriptive; only results/e3 (test, evaluated once after the dev freeze line in tasks/hpc_log.md) is confirmatory.

## Run inventory (runs with a readout on this split)

(no protocol runs found)

Base prior covariate r_0: qwen3-4b.base_B_s0 (150 complete families without the mass gate).

## Verdicts (rule 7; descriptive on dev)

pending: no student runs

Descriptive (no verdict): homogenization index, joint partial D per version, suggestibility per version, content and register checks of the training files.

## Seed-pair null: the same quantity between two O seeds of one teacher, pooled over teachers (seed_pair_null.csv)

(empty)

## (1) Cross-student disagreement: share of (family, variant) cells with different majority acts, same teacher and seed (disagreement.csv; disagree_conf = cells where both |p - 0.5| >= 0.1, robustness)

pending (needs two versions of the same teacher and seed)

## (2) Consistency change V - O, paired by seed (consistency_delta.csv; flip = flip rate, jsd = cross-framing JSD)

pending (no F / C run paired with an O run)

## (3) Teacher agreement change and excess teacher drift V - O, paired by seed (drift.csv; agree = majority-act agreement with the own teacher, jsd = JSD to the own teacher)

pending

## (4) Homogenization index per version: distance between students of different teachers, seed-matched (homogenization.csv; a fix that homogenises shows a drop vs O; 1 - corr is scale-free and is the index to read first)

pending (needs >= 2 teachers at the same seed)

## (5) Inheritance by form: delta_rho partial given r_0 of V minus O, paired by seed (inheritance_by_form.csv)

pending

### Joint partial D per version (joint_D_by_version.csv; e2 secondary statistic computed on each version's seed-pooled students)

pending (needs >= 2 teachers with runs of the version)

### Suggestibility s = delta(T5) - delta(T6) per (teacher, version) group with family-bootstrap CI (suggestibility_by_version.csv) and version differences (suggestibility_version_diffs.csv)

pending

## (6) Stage-2 content check of the ACTUAL training files (content_check.csv; docs/03 §5: a change here = content drift, not form)

| teacher | version | n_items | n_families | same_prompt_set_as_O | letter_identity_with_O | letter_matches_rewrite | kept_attempt_found | check_choice | check_reasons | check_conditions | check_strength | check_style | check_format | mean_attempts | kept_share | mean_words | mean_chars | mean_target_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt4o | O | 5132 | 1463 | True | 1.000 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 37.936 | 245.656 | 48.326 |
| gpt4o | F | 5132 | 1463 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.631 | 0.954 | 38.331 | 252.259 | 48.681 |
| gpt4o | C | 5132 | 1463 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.296 | 0.935 | 38.932 | 229.276 | 49.987 |
| claude46 | O | 4682 | 1469 | True | 1.000 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 62.258 | 412.116 | 77.481 |
| claude46 | F | 4682 | 1469 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 2.055 | 0.932 | 62.510 | 423.308 | 77.880 |
| claude46 | C | 4682 | 1469 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.546 | 0.856 | 64.066 | 377.250 | 79.326 |
| deepseek_v4 | O | 4668 | 1411 | True | 1.000 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 33.168 | 216.075 | 43.634 |
| deepseek_v4 | F | 4668 | 1411 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.569 | 0.972 | 33.910 | 226.935 | 44.425 |
| deepseek_v4 | C | 4668 | 1411 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.291 | 0.960 | 35.558 | 209.403 | 46.604 |

Letter identity with O: 100% for every F / C file.

**letter_matches_rewrite < 1 for 1 file(s)** (SFT letter differs from the kept rewrite text's leading 'Answer: X' (format leak in the rewrite, letter itself still equals O)): claude46 C 0.99979 (~1 item(s))

### Lexical register per version (register_check.csv; rates per word; fk_grade = Flesch-Kincaid proxy) and F vs C separability (register_separation.csv; frozen bar >= 0.90, e3_plan §2; Wilson 95% CIs)

| teacher | version | n | n_words | n_sentences | contraction_rate | formal_connective_rate | formal_word_rate | mean_word_len | words_per_sentence | fk_grade |
|---|---|---|---|---|---|---|---|---|---|---|
| gpt4o | O | 5132 | 38.222 | 1.835 | 0.005 | 0.002 | 0.050 | 5.393 | 21.799 | 13.989 |
| gpt4o | F | 5132 | 38.610 | 1.835 | 2.1e-04 | 0.004 | 0.055 | 5.498 | 22.010 | 14.656 |
| gpt4o | C | 5132 | 39.178 | 1.913 | 0.034 | 2.6e-04 | 0.012 | 4.811 | 21.139 | 10.374 |
| claude46 | O | 4682 | 62.694 | 2.905 | 0.003 | 0.002 | 0.028 | 5.492 | 21.759 | 14.438 |
| claude46 | F | 4682 | 63.046 | 2.900 | 3.8e-04 | 0.004 | 0.034 | 5.636 | 21.924 | 15.238 |
| claude46 | C | 4682 | 64.457 | 2.905 | 0.022 | 1.7e-04 | 0.006 | 4.779 | 22.365 | 10.775 |
| deepseek_v4 | O | 4668 | 33.969 | 1.516 | 9.4e-05 | 6.1e-04 | 0.031 | 5.333 | 23.931 | 14.548 |
| deepseek_v4 | F | 4668 | 34.340 | 1.515 | 1.3e-04 | 0.004 | 0.040 | 5.577 | 24.207 | 15.754 |
| deepseek_v4 | C | 4668 | 35.935 | 1.697 | 0.032 | 1.1e-04 | 0.007 | 4.784 | 22.514 | 10.773 |

| teacher | a | b | n_a | n_b | nearest_centroid_loo_acc | nc_ci_lo | nc_ci_hi | logistic_cv_acc | lr_ci_lo | lr_ci_hi | min_acc | status | top_feature |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt4o | F | C | 5132 | 5132 | 0.921 | 0.916 | 0.926 | 0.959 | 0.955 | 0.963 | 0.900 | pass | contraction_rate d=-2.10 |
| gpt4o | O | F | 5132 | 5132 | 0.591 | 0.581 | 0.600 | 0.595 | 0.585 | 0.604 | 0.900 | descriptive | contraction_rate d=0.55 |
| gpt4o | O | C | 5132 | 5132 | 0.879 | 0.872 | 0.885 | 0.903 | 0.897 | 0.908 | 0.900 | descriptive | contraction_rate d=-1.62 |
| claude46 | F | C | 4682 | 4682 | 0.927 | 0.921 | 0.932 | 0.952 | 0.948 | 0.957 | 0.900 | pass | mean_word_len d=2.08 |
| claude46 | O | F | 4682 | 4682 | 0.605 | 0.595 | 0.615 | 0.605 | 0.595 | 0.615 | 0.900 | descriptive | contraction_rate d=0.48 |
| claude46 | O | C | 4682 | 4682 | 0.886 | 0.879 | 0.892 | 0.900 | 0.894 | 0.906 | 0.900 | descriptive | mean_word_len d=1.77 |
| deepseek_v4 | F | C | 4668 | 4668 | 0.907 | 0.901 | 0.913 | 0.942 | 0.937 | 0.946 | 0.900 | pass | contraction_rate d=-1.75 |
| deepseek_v4 | O | F | 4668 | 4668 | 0.607 | 0.597 | 0.617 | 0.612 | 0.602 | 0.622 | 0.900 | descriptive | mean_word_len d=-0.46 |
| deepseek_v4 | O | C | 4668 | 4668 | 0.864 | 0.857 | 0.871 | 0.918 | 0.912 | 0.923 | 0.900 | descriptive | contraction_rate d=-1.75 |

The >= 0.90 bar applies to F vs C (pass / fail); O vs F and O vs C are descriptive (O is already a formal register, so O vs F near chance is expected and O vs C mirrors F vs C).

Notes: students are compared within teacher and paired by seed; the paired O students (runs/qwen3-4b-paired) are trained on the prompt intersection of O / F / C, not on the full O set of E1. 
Consistency is never read alone: every consistency row sits next to the agreement / JSD rows of the same runs. R students and the base are not E3 cells.