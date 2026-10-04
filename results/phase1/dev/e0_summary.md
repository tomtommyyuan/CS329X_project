# E0 summary (auto-generated)

## E0.3 type effects delta(j) with 95% bootstrap CI

| teacher | variant | delta | CI | n families | systematic |
|---|---|---|---|---|---|
| claude46 | T1 | 0.006 | [-0.007, 0.020] | 148 | no |
| claude46 | T3 | 0.012 | [-0.004, 0.030] | 148 | no |
| claude46 | T5 | 0.019 | [0.004, 0.035] | 148 | no |
| claude46 | T6 | -0.037 | [-0.065, -0.012] | 148 | no |
| deepseek_v4 | T1 | 0.014 | [0.002, 0.027] | 149 | no |
| deepseek_v4 | T3 | 0.007 | [-0.010, 0.023] | 149 | no |
| deepseek_v4 | T5 | 0.060 | [0.046, 0.074] | 149 | yes |
| deepseek_v4 | T6 | -0.081 | [-0.101, -0.061] | 149 | yes |
| gpt4o | T1 | 0.008 | [-0.003, 0.018] | 140 | no |
| gpt4o | T3 | 0.011 | [-0.003, 0.026] | 140 | no |
| gpt4o | T5 | 0.029 | [0.015, 0.044] | 140 | no |
| gpt4o | T6 | -0.048 | [-0.069, -0.029] | 140 | no |

## Suggestibility: delta(T5 'Should you do it?') minus delta(T6 'Should you not do it?'), in positive-act coordinates

- claude46: 0.056 (T5 0.019, T6 -0.037)
- deepseek_v4: 0.140 (T5 0.060, T6 -0.081)
- gpt4o: 0.077 (T5 0.029, T6 -0.048)

## Teacher consistency across profile framings (profile mode, symmetrized)

| teacher | families | uncertain cells (0.05<p<0.95) | pairwise flip rate | families with any flip | mean cross-framing JSD |
|---|---|---|---|---|---|
| claude46 | 148 | 0.080 | 0.073 | 0.135 | 0.042 |
| deepseek_v4 | 149 | 0.424 | 0.107 | 0.188 | 0.036 |
| gpt4o | 140 | 0.125 | 0.052 | 0.100 | 0.029 |

## Order artifact: mean |p(order1) - p(order2)| and position bias P(choose A)

- claude46: artifact 0.072, P(choose A) = 0.507 over 597 cells
- deepseek_v4: artifact 0.174, P(choose A) = 0.440 over 599 cells
- gpt4o: artifact 0.058, P(choose A) = 0.483 over 576 cells

## E0.3 profile reliability

| teacher | split-half by order (SB-corrected) | test-retest across passes | gate |
|---|---|---|---|
| claude46 | 0.383 (n=592) | 0.993 | FAIL/na |
| deepseek_v4 | 0.515 (n=596) | nan | ok |
| gpt4o | 0.675 (n=560) | nan | ok |

## E0.4 teacher distinctness

residual = profile after removing each teacher's own type effects delta(j); the raw correlation includes the direction shared by all teachers.

| A | B | cells | profile Pearson | residual Pearson | profile Spearman | majority agreement | gate |
|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 588 | 0.231 | 0.169 | 0.192 | 0.835 | ok |
| claude46 | gpt4o | 556 | 0.282 | 0.241 | 0.273 | 0.888 | ok |
| deepseek_v4 | gpt4o | 560 | 0.430 | 0.343 | 0.467 | 0.889 | ok |

## Pairwise framing flip rates (share of families whose majority action differs)

| teacher | T1-T3 | T1-T5 | T1-T6 | T3-T5 | T3-T6 | T5-T6 |
|---|---|---|---|---|---|---|
| claude46 | 0.054 | 0.027 | 0.101 | 0.054 | 0.101 | 0.101 |
| deepseek_v4 | 0.094 | 0.074 | 0.114 | 0.074 | 0.141 | 0.148 |
| gpt4o | 0.043 | 0.036 | 0.064 | 0.036 | 0.079 | 0.057 |

## Do teachers flip on the same families? (Jaccard of flipping-family sets)

| A | B | flips A | flips B | shared | Jaccard |
|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 20 | 28 | 9 | 0.231 |
| claude46 | gpt4o | 20 | 14 | 7 | 0.259 |
| deepseek_v4 | gpt4o | 28 | 14 | 7 | 0.200 |

## T0 (free rephrase) vs T1: mean |p_T0 - p_T1|

- claude46: 0.078 over 149 families
- deepseek_v4: 0.080 over 150 families
- gpt4o: 0.030 over 140 families
