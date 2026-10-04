# E0 summary (auto-generated)

## E0.1 answer rates by teacher x source (demo, T=0)

| teacher | source | answer | refusal | insufficient | malformed | n | gate |
|---|---|---|---|---|---|---|---|
| claude46 | daily_dilemmas | 0.998 | 0.002 | 0.000 | 0.000 | 600 | ok |
| claude46 | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 400 | ok |
| claude46 | valueconsistency | 0.975 | 0.025 | 0.000 | 0.000 | 40 | ok |
| claude_haiku45 | daily_dilemmas | 0.977 | 0.019 | 0.004 | 0.000 | 480 | ok |
| claude_haiku45 | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 320 | ok |
| claude_haiku45 | valueconsistency | 0.875 | 0.075 | 0.025 | 0.025 | 40 | ok |
| deepseek_v4 | daily_dilemmas | 1.000 | 0.000 | 0.000 | 0.000 | 600 | ok |
| deepseek_v4 | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 400 | ok |
| deepseek_v4 | valueconsistency | 1.000 | 0.000 | 0.000 | 0.000 | 40 | ok |
| gpt41 | daily_dilemmas | 0.996 | 0.004 | 0.000 | 0.000 | 480 | ok |
| gpt41 | moralchoice | 0.997 | 0.003 | 0.000 | 0.000 | 320 | ok |
| gpt41 | valueconsistency | 1.000 | 0.000 | 0.000 | 0.000 | 40 | ok |
| gpt4_0613 | daily_dilemmas | 0.975 | 0.023 | 0.002 | 0.000 | 480 | ok |
| gpt4_0613 | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 320 | ok |
| gpt4_0613 | valueconsistency | 0.900 | 0.100 | 0.000 | 0.000 | 40 | ok |
| gpt4o | daily_dilemmas | 1.000 | 0.000 | 0.000 | 0.000 | 600 | ok |
| gpt4o | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 400 | ok |
| gpt4o | valueconsistency | 1.000 | 0.000 | 0.000 | 0.000 | 40 | ok |
| gpt4o_mini | daily_dilemmas | 1.000 | 0.000 | 0.000 | 0.000 | 480 | ok |
| gpt4o_mini | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 320 | ok |
| gpt4o_mini | valueconsistency | 1.000 | 0.000 | 0.000 | 0.000 | 40 | ok |

## E0.2 order stability (demo, two_action)

| teacher | items | both answered | stable rate | gate |
|---|---|---|---|---|
| claude46 | 500 | 499 | 0.960 | ok |
| claude_haiku45 | 396 | 393 | 0.939 | ok |
| deepseek_v4 | 500 | 500 | 0.832 | ok |
| gpt41 | 399 | 398 | 0.950 | ok |
| gpt4_0613 | 396 | 392 | 0.939 | ok |
| gpt4o | 500 | 500 | 0.962 | ok |
| gpt4o_mini | 400 | 400 | 0.902 | ok |

## E0.3 type effects delta(j) with 95% bootstrap CI

| teacher | variant | delta | CI | n families | systematic |
|---|---|---|---|---|---|
| claude46 | T1 | 0.011 | [-0.004, 0.029] | 99 | no |
| claude46 | T3 | 0.010 | [-0.010, 0.031] | 99 | no |
| claude46 | T5 | 0.004 | [-0.010, 0.017] | 99 | no |
| claude46 | T6 | -0.025 | [-0.047, -0.007] | 99 | no |
| claude_haiku45 | T1 | 0.006 | [-0.006, 0.019] | 99 | no |
| claude_haiku45 | T3 | -0.007 | [-0.028, 0.015] | 99 | no |
| claude_haiku45 | T5 | 0.018 | [0.005, 0.033] | 99 | no |
| claude_haiku45 | T6 | -0.017 | [-0.035, -0.002] | 99 | no |
| deepseek_v4 | T1 | 0.023 | [0.008, 0.038] | 100 | no |
| deepseek_v4 | T3 | 0.039 | [0.016, 0.063] | 100 | no |
| deepseek_v4 | T5 | 0.048 | [0.028, 0.068] | 100 | no |
| deepseek_v4 | T6 | -0.110 | [-0.139, -0.083] | 100 | yes |
| gpt41 | T1 | 0.019 | [0.002, 0.037] | 98 | no |
| gpt41 | T3 | 0.011 | [-0.011, 0.031] | 98 | no |
| gpt41 | T5 | 0.026 | [0.007, 0.046] | 98 | no |
| gpt41 | T6 | -0.056 | [-0.089, -0.025] | 98 | yes |
| gpt4_0613 | T1 | 0.004 | [-0.008, 0.015] | 97 | no |
| gpt4_0613 | T3 | 0.013 | [-0.008, 0.036] | 97 | no |
| gpt4_0613 | T5 | 0.006 | [-0.009, 0.021] | 97 | no |
| gpt4_0613 | T6 | -0.023 | [-0.044, -0.004] | 97 | no |
| gpt4o | T1 | 0.009 | [-0.002, 0.020] | 97 | no |
| gpt4o | T3 | 0.016 | [0.004, 0.031] | 97 | no |
| gpt4o | T5 | 0.020 | [0.010, 0.031] | 97 | no |
| gpt4o | T6 | -0.045 | [-0.073, -0.022] | 97 | no |
| gpt4o_mini | T1 | 0.029 | [0.013, 0.047] | 100 | no |
| gpt4o_mini | T3 | 0.020 | [-0.003, 0.047] | 100 | no |
| gpt4o_mini | T5 | 0.019 | [0.003, 0.034] | 100 | no |
| gpt4o_mini | T6 | -0.069 | [-0.101, -0.039] | 100 | yes |

## Suggestibility: delta(T5 'Should you do it?') minus delta(T6 'Should you not do it?'), in positive-act coordinates

- claude46: 0.030 (T5 0.004, T6 -0.025)
- claude_haiku45: 0.036 (T5 0.018, T6 -0.017)
- deepseek_v4: 0.158 (T5 0.048, T6 -0.110)
- gpt41: 0.082 (T5 0.026, T6 -0.056)
- gpt4_0613: 0.029 (T5 0.006, T6 -0.023)
- gpt4o: 0.065 (T5 0.020, T6 -0.045)
- gpt4o_mini: 0.087 (T5 0.019, T6 -0.069)

## Teacher consistency across profile framings (profile mode, symmetrized)

| teacher | families | uncertain cells (0.05<p<0.95) | pairwise flip rate | families with any flip | mean cross-framing JSD |
|---|---|---|---|---|---|
| claude46 | 99 | 0.043 | 0.051 | 0.091 | 0.026 |
| claude_haiku45 | 99 | 0.091 | 0.052 | 0.091 | 0.021 |
| deepseek_v4 | 100 | 0.432 | 0.140 | 0.260 | 0.045 |
| gpt41 | 98 | 0.088 | 0.060 | 0.112 | 0.043 |
| gpt4_0613 | 97 | 0.138 | 0.040 | 0.072 | 0.024 |
| gpt4o | 97 | 0.088 | 0.050 | 0.093 | 0.022 |
| gpt4o_mini | 100 | 0.163 | 0.095 | 0.180 | 0.045 |

## Order artifact: mean |p(order1) - p(order2)| and position bias P(choose A)

- claude46: artifact 0.038, P(choose A) = 0.505 over 399 cells
- claude_haiku45: artifact 0.066, P(choose A) = 0.516 over 396 cells
- deepseek_v4: artifact 0.165, P(choose A) = 0.437 over 400 cells
- gpt41: artifact 0.053, P(choose A) = 0.493 over 398 cells
- gpt4_0613: artifact 0.064, P(choose A) = 0.490 over 392 cells
- gpt4o: artifact 0.037, P(choose A) = 0.484 over 396 cells
- gpt4o_mini: artifact 0.099, P(choose A) = 0.466 over 400 cells

## E0.3 profile reliability

| teacher | split-half by order (SB-corrected) | test-retest across passes | gate |
|---|---|---|---|
| claude46 | 0.357 (n=396) | 0.997 | FAIL/na |
| claude_haiku45 | 0.265 (n=396) | 0.923 | FAIL/na |
| deepseek_v4 | 0.627 (n=400) | nan | ok |
| gpt41 | 0.579 (n=392) | nan | ok |
| gpt4_0613 | 0.504 (n=388) | nan | ok |
| gpt4o | 0.726 (n=388) | nan | ok |
| gpt4o_mini | 0.645 (n=400) | nan | ok |

## E0.4 teacher distinctness

residual = profile after removing each teacher's own type effects delta(j); the raw correlation includes the direction shared by all teachers.

| A | B | cells | profile Pearson | residual Pearson | profile Spearman | majority agreement | gate |
|---|---|---|---|---|---|---|---|
| claude46 | claude_haiku45 | 396 | 0.198 | 0.187 | 0.186 | 0.871 | ok |
| claude46 | deepseek_v4 | 396 | 0.202 | 0.147 | 0.159 | 0.859 | ok |
| claude46 | gpt41 | 392 | 0.294 | 0.265 | 0.072 | 0.890 | ok |
| claude46 | gpt4_0613 | 388 | 0.225 | 0.208 | 0.169 | 0.905 | ok |
| claude46 | gpt4o | 388 | 0.255 | 0.222 | 0.173 | 0.905 | ok |
| claude46 | gpt4o_mini | 396 | 0.141 | 0.097 | 0.096 | 0.831 | ok |
| claude_haiku45 | deepseek_v4 | 396 | 0.191 | 0.150 | 0.063 | 0.831 | ok |
| claude_haiku45 | gpt41 | 392 | 0.180 | 0.151 | 0.051 | 0.867 | ok |
| claude_haiku45 | gpt4_0613 | 388 | 0.243 | 0.233 | 0.105 | 0.861 | ok |
| claude_haiku45 | gpt4o | 388 | 0.147 | 0.112 | 0.110 | 0.887 | ok |
| claude_haiku45 | gpt4o_mini | 396 | 0.011 | -0.028 | 0.094 | 0.808 | ok |
| deepseek_v4 | gpt41 | 392 | 0.349 | 0.260 | 0.473 | 0.855 | ok |
| deepseek_v4 | gpt4_0613 | 388 | 0.213 | 0.164 | 0.364 | 0.856 | ok |
| deepseek_v4 | gpt4o | 388 | 0.396 | 0.294 | 0.534 | 0.887 | ok |
| deepseek_v4 | gpt4o_mini | 400 | 0.495 | 0.416 | 0.497 | 0.843 | ok |
| gpt41 | gpt4_0613 | 384 | 0.327 | 0.302 | 0.429 | 0.883 | ok |
| gpt41 | gpt4o | 384 | 0.530 | 0.485 | 0.551 | 0.932 | ok |
| gpt41 | gpt4o_mini | 392 | 0.135 | 0.055 | 0.434 | 0.867 | ok |
| gpt4_0613 | gpt4o | 380 | 0.177 | 0.138 | 0.523 | 0.897 | ok |
| gpt4_0613 | gpt4o_mini | 388 | 0.201 | 0.167 | 0.315 | 0.853 | ok |
| gpt4o | gpt4o_mini | 388 | 0.165 | 0.077 | 0.382 | 0.884 | ok |

## Pairwise framing flip rates (share of families whose majority action differs)

| teacher | T1-T3 | T1-T5 | T1-T6 | T3-T5 | T3-T6 | T5-T6 |
|---|---|---|---|---|---|---|
| claude46 | 0.051 | 0.020 | 0.071 | 0.051 | 0.061 | 0.051 |
| claude_haiku45 | 0.081 | 0.030 | 0.040 | 0.071 | 0.061 | 0.030 |
| deepseek_v4 | 0.070 | 0.110 | 0.180 | 0.120 | 0.170 | 0.190 |
| gpt41 | 0.020 | 0.031 | 0.082 | 0.051 | 0.102 | 0.071 |
| gpt4_0613 | 0.041 | 0.010 | 0.041 | 0.031 | 0.062 | 0.052 |
| gpt4o | 0.031 | 0.041 | 0.062 | 0.031 | 0.072 | 0.062 |
| gpt4o_mini | 0.070 | 0.010 | 0.130 | 0.060 | 0.160 | 0.140 |

## Do teachers flip on the same families? (Jaccard of flipping-family sets)

| A | B | flips A | flips B | shared | Jaccard |
|---|---|---|---|---|---|
| claude46 | claude_haiku45 | 9 | 9 | 3 | 0.200 |
| claude46 | deepseek_v4 | 9 | 26 | 6 | 0.207 |
| claude46 | gpt41 | 9 | 11 | 5 | 0.333 |
| claude46 | gpt4_0613 | 9 | 7 | 4 | 0.333 |
| claude46 | gpt4o | 9 | 9 | 2 | 0.125 |
| claude46 | gpt4o_mini | 9 | 18 | 2 | 0.080 |
| claude_haiku45 | deepseek_v4 | 9 | 26 | 6 | 0.207 |
| claude_haiku45 | gpt41 | 9 | 11 | 3 | 0.176 |
| claude_haiku45 | gpt4_0613 | 9 | 7 | 3 | 0.231 |
| claude_haiku45 | gpt4o | 9 | 9 | 5 | 0.385 |
| claude_haiku45 | gpt4o_mini | 9 | 18 | 3 | 0.125 |
| deepseek_v4 | gpt41 | 26 | 11 | 6 | 0.194 |
| deepseek_v4 | gpt4_0613 | 26 | 7 | 5 | 0.179 |
| deepseek_v4 | gpt4o | 26 | 9 | 6 | 0.207 |
| deepseek_v4 | gpt4o_mini | 26 | 18 | 10 | 0.294 |
| gpt41 | gpt4_0613 | 11 | 7 | 3 | 0.200 |
| gpt41 | gpt4o | 11 | 9 | 4 | 0.250 |
| gpt41 | gpt4o_mini | 11 | 18 | 3 | 0.115 |
| gpt4_0613 | gpt4o | 7 | 9 | 2 | 0.143 |
| gpt4_0613 | gpt4o_mini | 7 | 18 | 4 | 0.190 |
| gpt4o | gpt4o_mini | 9 | 18 | 4 | 0.174 |

## T0 (free rephrase) vs T1: mean |p_T0 - p_T1|

- claude46: 0.069 over 100 families
- deepseek_v4: 0.096 over 100 families
- gpt4o: 0.061 over 99 families
