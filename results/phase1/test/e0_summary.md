# E0 summary (auto-generated)

## E0.3 type effects delta(j) with 95% bootstrap CI

| teacher | variant | delta | CI | n families | systematic |
|---|---|---|---|---|---|
| claude46 | T1 | 0.002 | [-0.008, 0.013] | 297 | no |
| claude46 | T3 | -0.001 | [-0.013, 0.010] | 297 | no |
| claude46 | T5 | 0.023 | [0.011, 0.036] | 297 | no |
| claude46 | T6 | -0.024 | [-0.039, -0.011] | 297 | no |
| deepseek_v4 | T1 | 0.011 | [0.003, 0.018] | 300 | no |
| deepseek_v4 | T3 | 0.015 | [0.004, 0.026] | 300 | no |
| deepseek_v4 | T5 | 0.044 | [0.036, 0.053] | 300 | no |
| deepseek_v4 | T6 | -0.070 | [-0.082, -0.057] | 300 | yes |
| gpt4o | T1 | 0.006 | [-0.001, 0.012] | 291 | no |
| gpt4o | T3 | 0.000 | [-0.009, 0.010] | 291 | no |
| gpt4o | T5 | 0.028 | [0.019, 0.039] | 291 | no |
| gpt4o | T6 | -0.034 | [-0.047, -0.023] | 291 | no |

## Suggestibility: delta(T5 'Should you do it?') minus delta(T6 'Should you not do it?'), in positive-act coordinates

- claude46: 0.048 (T5 0.023, T6 -0.024)
- deepseek_v4: 0.114 (T5 0.044, T6 -0.070)
- gpt4o: 0.062 (T5 0.028, T6 -0.034)

## Teacher consistency across profile framings (profile mode, symmetrized)

| teacher | families | uncertain cells (0.05<p<0.95) | pairwise flip rate | families with any flip | mean cross-framing JSD |
|---|---|---|---|---|---|
| claude46 | 297 | 0.084 | 0.060 | 0.111 | 0.037 |
| deepseek_v4 | 300 | 0.371 | 0.066 | 0.123 | 0.031 |
| gpt4o | 291 | 0.106 | 0.044 | 0.086 | 0.023 |

## Order artifact: mean |p(order1) - p(order2)| and position bias P(choose A)

- claude46: artifact 0.069, P(choose A) = 0.503 over 1194 cells
- deepseek_v4: artifact 0.149, P(choose A) = 0.454 over 1200 cells
- gpt4o: artifact 0.041, P(choose A) = 0.490 over 1184 cells

## E0.3 profile reliability

| teacher | split-half by order (SB-corrected) | test-retest across passes | gate |
|---|---|---|---|
| claude46 | 0.329 (n=1188) | 0.990 | FAIL/na |
| deepseek_v4 | 0.466 (n=1200) | nan | FAIL/na |
| gpt4o | 0.691 (n=1164) | nan | ok |

## E0.4 teacher distinctness

residual = profile after removing each teacher's own type effects delta(j); the raw correlation includes the direction shared by all teachers.

| A | B | cells | profile Pearson | residual Pearson | profile Spearman | majority agreement | gate |
|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 1188 | 0.246 | 0.203 | 0.194 | 0.902 | ok |
| claude46 | gpt4o | 1160 | 0.277 | 0.249 | 0.254 | 0.910 | ok |
| deepseek_v4 | gpt4o | 1164 | 0.347 | 0.275 | 0.495 | 0.922 | ok |

## Pairwise framing flip rates (share of families whose majority action differs)

| teacher | T1-T3 | T1-T5 | T1-T6 | T3-T5 | T3-T6 | T5-T6 |
|---|---|---|---|---|---|---|
| claude46 | 0.051 | 0.047 | 0.067 | 0.057 | 0.064 | 0.074 |
| deepseek_v4 | 0.043 | 0.030 | 0.083 | 0.060 | 0.093 | 0.087 |
| gpt4o | 0.014 | 0.024 | 0.055 | 0.038 | 0.062 | 0.072 |

## Do teachers flip on the same families? (Jaccard of flipping-family sets)

| A | B | flips A | flips B | shared | Jaccard |
|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 33 | 37 | 12 | 0.207 |
| claude46 | gpt4o | 33 | 25 | 9 | 0.184 |
| deepseek_v4 | gpt4o | 37 | 25 | 13 | 0.265 |

## T0 (free rephrase) vs T1: mean |p_T0 - p_T1|

- claude46: 0.051 over 297 families
- deepseek_v4: 0.061 over 300 families
- gpt4o: 0.040 over 292 families
