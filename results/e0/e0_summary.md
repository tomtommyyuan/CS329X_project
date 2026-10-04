# E0 summary (auto-generated)

## E0.1 answer rates by teacher x source (demo, T=0)

| teacher | source | answer | refusal | insufficient | malformed | n | gate |
|---|---|---|---|---|---|---|---|
| claude46 | daily_dilemmas | 0.998 | 0.002 | 0.000 | 0.000 | 480 | ok |
| claude46 | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 320 | ok |
| claude46 | valueconsistency | 0.975 | 0.025 | 0.000 | 0.000 | 40 | ok |
| claude_haiku45 | daily_dilemmas | 0.975 | 0.019 | 0.006 | 0.000 | 480 | ok |
| claude_haiku45 | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 320 | ok |
| claude_haiku45 | valueconsistency | 0.875 | 0.075 | 0.025 | 0.025 | 40 | ok |
| deepseek_v4 | daily_dilemmas | 1.000 | 0.000 | 0.000 | 0.000 | 480 | ok |
| deepseek_v4 | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 320 | ok |
| deepseek_v4 | valueconsistency | 1.000 | 0.000 | 0.000 | 0.000 | 40 | ok |
| gpt41 | daily_dilemmas | 0.996 | 0.004 | 0.000 | 0.000 | 480 | ok |
| gpt41 | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 320 | ok |
| gpt41 | valueconsistency | 1.000 | 0.000 | 0.000 | 0.000 | 40 | ok |
| gpt4_0613 | daily_dilemmas | 0.967 | 0.031 | 0.002 | 0.000 | 480 | ok |
| gpt4_0613 | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 320 | ok |
| gpt4_0613 | valueconsistency | 0.900 | 0.100 | 0.000 | 0.000 | 40 | ok |
| gpt4o | daily_dilemmas | 1.000 | 0.000 | 0.000 | 0.000 | 480 | ok |
| gpt4o | moralchoice | 0.997 | 0.003 | 0.000 | 0.000 | 320 | ok |
| gpt4o | valueconsistency | 1.000 | 0.000 | 0.000 | 0.000 | 40 | ok |
| gpt4o_mini | daily_dilemmas | 1.000 | 0.000 | 0.000 | 0.000 | 480 | ok |
| gpt4o_mini | moralchoice | 1.000 | 0.000 | 0.000 | 0.000 | 320 | ok |
| gpt4o_mini | valueconsistency | 1.000 | 0.000 | 0.000 | 0.000 | 40 | ok |

## E0.2 order stability (demo, two_action)

| teacher | items | both answered | stable rate | gate |
|---|---|---|---|---|
| claude46 | 400 | 399 | 0.970 | ok |
| claude_haiku45 | 396 | 392 | 0.952 | ok |
| deepseek_v4 | 400 | 400 | 0.860 | ok |
| gpt41 | 399 | 399 | 0.960 | ok |
| gpt4_0613 | 394 | 390 | 0.962 | ok |
| gpt4o | 400 | 399 | 0.952 | ok |
| gpt4o_mini | 400 | 400 | 0.902 | ok |

## E0.3 type effects delta(j) with 95% bootstrap CI

| teacher | variant | delta | CI | n families | systematic |
|---|---|---|---|---|---|
| claude46 | T1 | -0.001 | [-0.020, 0.017] | 99 | no |
| claude46 | T2 | -0.010 | [-0.030, 0.009] | 99 | no |
| claude46 | T3 | 0.002 | [-0.024, 0.027] | 99 | no |
| claude46 | T4 | 0.010 | [-0.012, 0.033] | 99 | no |
| claude_haiku45 | T1 | 0.009 | [-0.003, 0.024] | 99 | no |
| claude_haiku45 | T2 | -0.012 | [-0.031, 0.006] | 99 | no |
| claude_haiku45 | T3 | 0.005 | [-0.012, 0.025] | 99 | no |
| claude_haiku45 | T4 | -0.002 | [-0.021, 0.016] | 99 | no |
| deepseek_v4 | T1 | -0.005 | [-0.017, 0.008] | 100 | no |
| deepseek_v4 | T2 | -0.003 | [-0.014, 0.008] | 100 | no |
| deepseek_v4 | T3 | 0.018 | [-0.004, 0.039] | 100 | no |
| deepseek_v4 | T4 | -0.010 | [-0.030, 0.009] | 100 | no |
| gpt41 | T1 | 0.007 | [-0.005, 0.021] | 98 | no |
| gpt41 | T2 | 0.001 | [-0.013, 0.016] | 98 | no |
| gpt41 | T3 | 0.002 | [-0.013, 0.019] | 98 | no |
| gpt41 | T4 | -0.010 | [-0.030, 0.007] | 98 | no |
| gpt4_0613 | T1 | -0.010 | [-0.023, 0.000] | 96 | no |
| gpt4_0613 | T2 | -0.001 | [-0.014, 0.011] | 96 | no |
| gpt4_0613 | T3 | 0.017 | [-0.001, 0.040] | 96 | no |
| gpt4_0613 | T4 | -0.006 | [-0.020, 0.008] | 96 | no |
| gpt4o | T1 | -0.005 | [-0.015, 0.002] | 95 | no |
| gpt4o | T2 | -0.005 | [-0.015, 0.003] | 95 | no |
| gpt4o | T3 | 0.005 | [-0.003, 0.016] | 95 | no |
| gpt4o | T4 | 0.005 | [-0.005, 0.018] | 95 | no |
| gpt4o_mini | T1 | -0.007 | [-0.025, 0.008] | 100 | no |
| gpt4o_mini | T2 | 0.006 | [-0.009, 0.022] | 100 | no |
| gpt4o_mini | T3 | 0.000 | [-0.021, 0.022] | 100 | no |
| gpt4o_mini | T4 | -0.000 | [-0.015, 0.013] | 100 | no |

## Teacher consistency across profile framings (profile mode, symmetrized)

| teacher | families | uncertain cells (0.05<p<0.95) | pairwise flip rate | families with any flip | mean cross-framing JSD |
|---|---|---|---|---|---|
| claude46 | 99 | 0.045 | 0.052 | 0.091 | 0.036 |
| claude_haiku45 | 99 | 0.081 | 0.052 | 0.091 | 0.022 |
| deepseek_v4 | 100 | 0.383 | 0.072 | 0.130 | 0.020 |
| gpt41 | 98 | 0.063 | 0.041 | 0.082 | 0.019 |
| gpt4_0613 | 96 | 0.114 | 0.028 | 0.052 | 0.019 |
| gpt4o | 95 | 0.081 | 0.035 | 0.063 | 0.007 |
| gpt4o_mini | 100 | 0.142 | 0.047 | 0.080 | 0.023 |

## Order artifact: mean |p(order1) - p(order2)| and position bias P(choose A)

- claude46: artifact 0.033, P(choose A) = 0.495 over 399 cells
- claude_haiku45: artifact 0.055, P(choose A) = 0.518 over 396 cells
- deepseek_v4: artifact 0.132, P(choose A) = 0.440 over 400 cells
- gpt41: artifact 0.041, P(choose A) = 0.498 over 398 cells
- gpt4_0613: artifact 0.050, P(choose A) = 0.484 over 387 cells
- gpt4o: artifact 0.035, P(choose A) = 0.484 over 394 cells
- gpt4o_mini: artifact 0.098, P(choose A) = 0.461 over 400 cells

## E0.3 profile reliability

| teacher | split-half by order (SB-corrected) | test-retest across passes | gate |
|---|---|---|---|
| claude46 | 0.667 (n=396) | 0.996 | ok |
| claude_haiku45 | 0.611 (n=396) | 0.931 | ok |
| deepseek_v4 | 0.668 (n=400) | nan | ok |
| gpt41 | 0.405 (n=392) | nan | FAIL/na |
| gpt4_0613 | 0.543 (n=384) | nan | ok |
| gpt4o | 0.571 (n=380) | nan | ok |
| gpt4o_mini | 0.433 (n=400) | nan | FAIL/na |

## E0.4 teacher distinctness

residual = profile after removing each teacher's own type effects delta(j); the raw correlation includes the direction shared by all teachers.

| A | B | cells | profile Pearson | residual Pearson | profile Spearman | majority agreement | gate |
|---|---|---|---|---|---|---|---|
| claude46 | claude_haiku45 | 396 | 0.167 | 0.166 | 0.080 | 0.884 | ok |
| claude46 | deepseek_v4 | 396 | 0.125 | 0.128 | 0.114 | 0.894 | ok |
| claude46 | gpt41 | 392 | 0.088 | 0.092 | 0.100 | 0.890 | ok |
| claude46 | gpt4_0613 | 384 | 0.205 | 0.204 | 0.148 | 0.898 | ok |
| claude46 | gpt4o | 380 | 0.243 | 0.240 | 0.231 | 0.908 | ok |
| claude46 | gpt4o_mini | 396 | 0.125 | 0.127 | 0.128 | 0.856 | ok |
| claude_haiku45 | deepseek_v4 | 396 | 0.190 | 0.188 | 0.104 | 0.874 | ok |
| claude_haiku45 | gpt41 | 392 | 0.052 | 0.049 | 0.067 | 0.890 | ok |
| claude_haiku45 | gpt4_0613 | 384 | 0.215 | 0.217 | 0.102 | 0.893 | ok |
| claude_haiku45 | gpt4o | 380 | -0.011 | -0.011 | 0.017 | 0.903 | ok |
| claude_haiku45 | gpt4o_mini | 396 | 0.130 | 0.136 | 0.077 | 0.841 | ok |
| deepseek_v4 | gpt41 | 392 | 0.094 | 0.090 | 0.168 | 0.880 | ok |
| deepseek_v4 | gpt4_0613 | 384 | 0.202 | 0.192 | 0.278 | 0.857 | ok |
| deepseek_v4 | gpt4o | 380 | 0.009 | 0.006 | 0.174 | 0.889 | ok |
| deepseek_v4 | gpt4o_mini | 400 | 0.328 | 0.330 | 0.308 | 0.838 | ok |
| gpt41 | gpt4_0613 | 380 | 0.060 | 0.060 | 0.230 | 0.905 | ok |
| gpt41 | gpt4o | 376 | 0.027 | 0.029 | 0.313 | 0.915 | ok |
| gpt41 | gpt4o_mini | 392 | 0.228 | 0.230 | 0.252 | 0.903 | ok |
| gpt4_0613 | gpt4o | 368 | 0.258 | 0.254 | 0.337 | 0.894 | ok |
| gpt4_0613 | gpt4o_mini | 384 | 0.108 | 0.106 | 0.176 | 0.865 | ok |
| gpt4o | gpt4o_mini | 380 | 0.032 | 0.033 | 0.258 | 0.889 | ok |

## Pairwise framing flip rates (share of families whose majority action differs)

| teacher | T1-T2 | T1-T3 | T1-T4 | T2-T3 | T2-T4 | T3-T4 |
|---|---|---|---|---|---|---|
| claude46 | 0.051 | 0.051 | 0.030 | 0.061 | 0.040 | 0.081 |
| claude_haiku45 | 0.040 | 0.061 | 0.030 | 0.061 | 0.051 | 0.071 |
| deepseek_v4 | 0.040 | 0.070 | 0.060 | 0.050 | 0.080 | 0.130 |
| gpt41 | 0.020 | 0.031 | 0.051 | 0.031 | 0.051 | 0.061 |
| gpt4_0613 | 0.021 | 0.031 | 0.031 | 0.031 | 0.010 | 0.042 |
| gpt4o | 0.021 | 0.042 | 0.021 | 0.042 | 0.042 | 0.042 |
| gpt4o_mini | 0.040 | 0.080 | 0.020 | 0.040 | 0.040 | 0.060 |

## Do teachers flip on the same families? (Jaccard of flipping-family sets)

| A | B | flips A | flips B | shared | Jaccard |
|---|---|---|---|---|---|
| claude46 | claude_haiku45 | 9 | 9 | 1 | 0.059 |
| claude46 | deepseek_v4 | 9 | 13 | 3 | 0.158 |
| claude46 | gpt41 | 9 | 8 | 2 | 0.133 |
| claude46 | gpt4_0613 | 9 | 5 | 3 | 0.273 |
| claude46 | gpt4o | 9 | 6 | 1 | 0.071 |
| claude46 | gpt4o_mini | 9 | 8 | 1 | 0.062 |
| claude_haiku45 | deepseek_v4 | 9 | 13 | 2 | 0.100 |
| claude_haiku45 | gpt41 | 9 | 8 | 2 | 0.133 |
| claude_haiku45 | gpt4_0613 | 9 | 5 | 2 | 0.167 |
| claude_haiku45 | gpt4o | 9 | 6 | 2 | 0.154 |
| claude_haiku45 | gpt4o_mini | 9 | 8 | 0 | 0.000 |
| deepseek_v4 | gpt41 | 13 | 8 | 2 | 0.105 |
| deepseek_v4 | gpt4_0613 | 13 | 5 | 4 | 0.286 |
| deepseek_v4 | gpt4o | 13 | 6 | 3 | 0.188 |
| deepseek_v4 | gpt4o_mini | 13 | 8 | 3 | 0.167 |
| gpt41 | gpt4_0613 | 8 | 5 | 1 | 0.083 |
| gpt41 | gpt4o | 8 | 6 | 2 | 0.167 |
| gpt41 | gpt4o_mini | 8 | 8 | 2 | 0.143 |
| gpt4_0613 | gpt4o | 5 | 6 | 1 | 0.100 |
| gpt4_0613 | gpt4o_mini | 5 | 8 | 1 | 0.083 |
| gpt4o | gpt4o_mini | 6 | 8 | 2 | 0.167 |
