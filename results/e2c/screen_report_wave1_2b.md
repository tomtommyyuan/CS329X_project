# E2c screening report

rule: contested = majorities differ between >= 2 teachers OR any logprob teacher p_sym in [0.2, 0.8]; Claude order split = contested; any non-answer -> excluded; families without a T1 prompt in --prompts = not_screened. teachers ['gpt4o', 'claude46', 'deepseek_v4']. excluded waves: none (0 families kept out of C and K).

bookkeeping (pool): {'families_without_any_demo': 0, 'families_not_screened': 7818, 'readouts': "{'claude46': 'sampling', 'deepseek_v4': 'logprobs', 'gpt4o': 'logprobs'}"}

bookkeeping (tier0): {'other_variant': 26874, 'families_without_any_demo': 0, 'families_not_screened': 0, 'readouts': "{'claude46': 'sampling', 'deepseek_v4': 'logprobs', 'gpt4o': 'logprobs'}"}

## Calibration: existing train (tier 0)

valid 1469, contested 356, consensus 1113, non-answer 24 (expected 1,469 / 356 / 1,113 / 24)

## Contested rate per set and source

| source | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aita_berkeley | 50 | 0 | 50 | 0 | 0.000 | 50 | 15 | 0.300 | 6 | 7 | 7 | 3 | 12 |
| daily_dilemmas | 1010 | 0 | 1010 | 6 | 0.006 | 1004 | 245 | 0.244 | 95 | 170 | 57 | 84 | 161 |
| hendrycks_ethics | 1948 | 48 | 1900 | 0 | 0.000 | 1900 | 695 | 0.366 | 192 | 541 | 155 | 298 | 397 |
| moral_stories | 7770 | 7770 | 0 | 0 | nan | 0 | 0 | nan | 0 | 0 | 0 | 0 | 0 |
| moralchoice | 1158 | 0 | 1158 | 19 | 0.016 | 1139 | 114 | 0.100 | 60 | 74 | 18 | 30 | 84 |
| scruples | 585 | 0 | 585 | 6 | 0.010 | 579 | 217 | 0.375 | 100 | 152 | 37 | 70 | 147 |

### set pool: by source

| source | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aita_berkeley | 50 | 0 | 50 | 0 | 0.000 | 50 | 15 | 0.300 | 6 | 7 | 7 | 3 | 12 |
| hendrycks_ethics | 1948 | 48 | 1900 | 0 | 0.000 | 1900 | 695 | 0.366 | 192 | 541 | 155 | 298 | 397 |
| moral_stories | 7770 | 7770 | 0 | 0 | nan | 0 | 0 | nan | 0 | 0 | 0 | 0 | 0 |
| moralchoice | 675 | 0 | 675 | 1 | 0.001 | 674 | 3 | 0.004 | 1 | 2 | 1 | 1 | 2 |
| scruples | 585 | 0 | 585 | 6 | 0.010 | 579 | 217 | 0.375 | 100 | 152 | 37 | 70 | 147 |

### set tier0: by source

| source | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| daily_dilemmas | 1010 | 0 | 1010 | 6 | 0.006 | 1004 | 245 | 0.244 | 95 | 170 | 57 | 84 | 161 |
| moralchoice | 483 | 0 | 483 | 18 | 0.037 | 465 | 111 | 0.239 | 59 | 72 | 17 | 29 | 82 |

## Per wave (pool)

| wave | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2210 | 600 | 1610 | 7 | 0.004 | 1603 | 344 | 0.215 | 138 | 250 | 63 | 125 | 219 |
| 2a | 2424 | 2424 | 0 | 0 | nan | 0 | 0 | nan | 0 | 0 | 0 | 0 | 0 |
| 2b | 1600 | 0 | 1600 | 0 | 0.000 | 1600 | 586 | 0.366 | 161 | 452 | 137 | 247 | 339 |
| reserve | 4794 | 4794 | 0 | 0 | nan | 0 | 0 | nan | 0 | 0 | 0 | 0 | 0 |

## Per human / construction prior

### aita_berkeley

| prior | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| prospective | 40 | 0 | 40 | 0 | 0.000 | 40 | 10 | 0.250 | 4 | 5 | 6 | 2 | 8 |
| prospective|human_contested | 9 | 0 | 9 | 0 | 0.000 | 9 | 5 | 0.556 | 2 | 2 | 1 | 1 | 4 |
| prospective|llm_differ | 1 | 0 | 1 | 0 | 0.000 | 1 | 0 | 0.000 | 0 | 0 | 0 | 0 | 0 |

### daily_dilemmas

| prior | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| daily_dilemmas:high | 1010 | 0 | 1010 | 6 | 0.006 | 1004 | 245 | 0.244 | 95 | 170 | 57 | 84 | 161 |

### hendrycks_ethics

| prior | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| consensus_x | 1137 | 33 | 1104 | 0 | 0.000 | 1104 | 366 | 0.332 | 110 | 266 | 102 | 132 | 234 |
| consensus_y | 811 | 15 | 796 | 0 | 0.000 | 796 | 329 | 0.413 | 82 | 275 | 53 | 166 | 163 |

### moral_stories

| prior | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| norm_negative|clean | 3952 | 3952 | 0 | 0 | nan | 0 | 0 | nan | 0 | 0 | 0 | 0 | 0 |
| norm_negative|same_gender_other | 1094 | 1094 | 0 | 0 | nan | 0 | 0 | nan | 0 | 0 | 0 | 0 | 0 |
| norm_positive|clean | 2143 | 2143 | 0 | 0 | nan | 0 | 0 | nan | 0 | 0 | 0 | 0 | 0 |
| norm_positive|same_gender_other | 581 | 581 | 0 | 0 | nan | 0 | 0 | nan | 0 | 0 | 0 | 0 | 0 |

### moralchoice

| prior | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| moralchoice:high | 483 | 0 | 483 | 18 | 0.037 | 465 | 111 | 0.239 | 59 | 72 | 17 | 29 | 82 |
| moralchoice:low | 675 | 0 | 675 | 1 | 0.001 | 674 | 3 | 0.004 | 1 | 2 | 1 | 1 | 2 |

### scruples

| prior | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| minority<0.3 | 472 | 0 | 472 | 5 | 0.011 | 467 | 167 | 0.358 | 78 | 114 | 33 | 50 | 117 |
| minority>=0.3 | 113 | 0 | 113 | 1 | 0.009 | 112 | 50 | 0.446 | 22 | 38 | 4 | 20 | 30 |

## Teacher pairwise disagreement (defined majorities, both answered)

set pool

| pair | n_families | n_differ | rate |
|---|---|---|---|
| gpt4o-claude46 | 3003 | 216 | 0.072 |
| gpt4o-deepseek_v4 | 2610 | 132 | 0.051 |
| claude46-deepseek_v4 | 2496 | 128 | 0.051 |

set tier0

| pair | n_families | n_differ | rate |
|---|---|---|---|
| gpt4o-claude46 | 1395 | 111 | 0.080 |
| gpt4o-deepseek_v4 | 1273 | 72 | 0.057 |
| claude46-deepseek_v4 | 1226 | 74 | 0.060 |

## Non-answer and p_x-missing counts per teacher (pool, screened families only)

| teacher | families not answered (either order) | answer rows without p_x |
|---|---|---|
| gpt4o | 4 | 0 |
| claude46 | 3 | 0 |
| deepseek_v4 | 0 | 0 |

## Exact order flips inside the band (pool)

band_exact_flip: logprob teacher with p_sym in [0.2, 0.8] and |p_o1 - p_o2| >= 0.9 (both orders confident, opposite). flip_only families are contested through such flips alone; the pre-registered sensitivity set is contested minus flip_only.

| teacher | answered | in band | exact flips | flip share |
|---|---|---|---|---|
| gpt4o | 3206 | 226 | 37 | 0.164 |
| claude46 | 3207 | 200 | 0 | 0.000 |
| deepseek_v4 | 3210 | 593 | 593 | 1.000 |

flip_only families: 372 of 930 contested

## p_sym distribution (pool, answered families)

gpt4o

| bin | families |
|---|---|
| [0.00, 0.05) | 870 |
| [0.05, 0.20) | 76 |
| [0.20, 0.35) | 49 |
| [0.35, 0.50) | 63 |
| [0.50, 0.65) | 59 |
| [0.65, 0.80) | 55 |
| [0.80, 0.95) | 118 |
| [0.95, 1.00] | 1913 |

claude46

| bin | families |
|---|---|
| [0.00, 0.05) | 1028 |
| [0.05, 0.20) | 0 |
| [0.20, 0.35) | 0 |
| [0.35, 0.50) | 0 |
| [0.50, 0.65) | 200 |
| [0.65, 0.80) | 0 |
| [0.80, 0.95) | 0 |
| [0.95, 1.00] | 1975 |

deepseek_v4

| bin | families |
|---|---|
| [0.00, 0.05) | 784 |
| [0.05, 0.20) | 0 |
| [0.20, 0.35) | 0 |
| [0.35, 0.50) | 0 |
| [0.50, 0.65) | 593 |
| [0.65, 0.80) | 0 |
| [0.80, 0.95) | 0 |
| [0.95, 1.00] | 1826 |

## Non-answer and p_x-missing counts per teacher (tier0, screened families only)

| teacher | families not answered (either order) | answer rows without p_x |
|---|---|---|
| gpt4o | 21 | 0 |
| claude46 | 3 | 0 |
| deepseek_v4 | 0 | 0 |

## Exact order flips inside the band (tier0)

band_exact_flip: logprob teacher with p_sym in [0.2, 0.8] and |p_o1 - p_o2| >= 0.9 (both orders confident, opposite). flip_only families are contested through such flips alone; the pre-registered sensitivity set is contested minus flip_only.

| teacher | answered | in band | exact flips | flip share |
|---|---|---|---|---|
| gpt4o | 1472 | 82 | 12 | 0.146 |
| claude46 | 1490 | 74 | 0 | 0.000 |
| deepseek_v4 | 1493 | 196 | 196 | 1.000 |

flip_only families: 113 of 356 contested

## p_sym distribution (tier0, answered families)

gpt4o

| bin | families |
|---|---|
| [0.00, 0.05) | 603 |
| [0.05, 0.20) | 42 |
| [0.20, 0.35) | 14 |
| [0.35, 0.50) | 24 |
| [0.50, 0.65) | 27 |
| [0.65, 0.80) | 17 |
| [0.80, 0.95) | 32 |
| [0.95, 1.00] | 710 |

claude46

| bin | families |
|---|---|
| [0.00, 0.05) | 620 |
| [0.05, 0.20) | 0 |
| [0.20, 0.35) | 0 |
| [0.35, 0.50) | 0 |
| [0.50, 0.65) | 74 |
| [0.65, 0.80) | 0 |
| [0.80, 0.95) | 0 |
| [0.95, 1.00] | 775 |

deepseek_v4

| bin | families |
|---|---|
| [0.00, 0.05) | 597 |
| [0.05, 0.20) | 0 |
| [0.20, 0.35) | 0 |
| [0.35, 0.50) | 0 |
| [0.50, 0.65) | 196 |
| [0.65, 0.80) | 0 |
| [0.80, 0.95) | 0 |
| [0.95, 1.00] | 676 |

## Selection

| set | families |
|---|---|
| tier0 contested (all) | 356 |
| pool contested available | 930 |
| pool contested chosen | 930 |
| target | 1500 |
| written (E2c-C) | 1286 |
| flip_only among written | 485 |

E2c-C composition and the matched E2c-K draw (consensus pool incl. tier 0, seed 20261002):

| source | C chosen | K target | K drawn | K available |
|---|---|---|---|---|
| aita_berkeley | 15 | 15 | 15 | 35 |
| daily_dilemmas | 245 | 245 | 245 | 759 |
| hendrycks_ethics | 695 | 695 | 695 | 1205 |
| moralchoice | 114 | 114 | 114 | 1025 |
| scruples | 217 | 217 | 217 | 362 |

K written: 1286 (not written; pass --consensus-select-out)
