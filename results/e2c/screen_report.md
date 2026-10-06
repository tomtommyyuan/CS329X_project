# E2c screening report

rule: contested = majorities differ between >= 2 teachers OR any logprob teacher p_sym in [0.2, 0.8]; Claude order split = contested; any non-answer -> excluded; families without a T1 prompt in --prompts = not_screened. teachers ['gpt4o', 'claude46', 'deepseek_v4']. excluded waves: none (0 families kept out of C and K).

bookkeeping (pool): {'families_without_any_demo': 0, 'families_not_screened': 3107, 'readouts': "{'deepseek_v4': 'logprobs', 'gpt4o': 'logprobs', 'claude46': 'sampling'}"}

bookkeeping (tier0): {'other_variant': 26874, 'families_without_any_demo': 0, 'families_not_screened': 0, 'readouts': "{'deepseek_v4': 'logprobs', 'gpt4o': 'logprobs', 'claude46': 'sampling'}"}

## Calibration: existing train (tier 0)

valid 1469, contested 356, consensus 1113, non-answer 24 (expected 1,469 / 356 / 1,113 / 24)

## Contested rate per set and source

| source | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aita_berkeley | 50 | 0 | 50 | 0 | 0.000 | 50 | 15 | 0.300 | 6 | 7 | 7 | 3 | 12 |
| daily_dilemmas | 1010 | 0 | 1010 | 6 | 0.006 | 1004 | 245 | 0.244 | 95 | 170 | 57 | 84 | 161 |
| hendrycks_ethics | 1948 | 48 | 1900 | 0 | 0.000 | 1900 | 695 | 0.366 | 192 | 541 | 155 | 298 | 397 |
| moral_stories | 5067 | 3059 | 2008 | 15 | 0.007 | 1993 | 199 | 0.100 | 67 | 136 | 43 | 68 | 131 |
| moralchoice | 1158 | 0 | 1158 | 19 | 0.016 | 1139 | 114 | 0.100 | 60 | 74 | 18 | 30 | 84 |
| scruples | 585 | 0 | 585 | 6 | 0.010 | 579 | 217 | 0.375 | 100 | 152 | 37 | 70 | 147 |

### set pool: by source

| source | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aita_berkeley | 50 | 0 | 50 | 0 | 0.000 | 50 | 15 | 0.300 | 6 | 7 | 7 | 3 | 12 |
| hendrycks_ethics | 1948 | 48 | 1900 | 0 | 0.000 | 1900 | 695 | 0.366 | 192 | 541 | 155 | 298 | 397 |
| moral_stories | 5067 | 3059 | 2008 | 15 | 0.007 | 1993 | 199 | 0.100 | 67 | 136 | 43 | 68 | 131 |
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
| 1 | 2103 | 3 | 2100 | 12 | 0.006 | 2088 | 392 | 0.188 | 156 | 277 | 77 | 135 | 257 |
| 2a | 1515 | 0 | 1515 | 10 | 0.007 | 1505 | 156 | 0.104 | 54 | 107 | 35 | 51 | 105 |
| 2b | 1600 | 44 | 1556 | 0 | 0.000 | 1556 | 568 | 0.365 | 151 | 443 | 130 | 249 | 319 |
| reserve | 3107 | 3060 | 47 | 0 | 0.000 | 47 | 13 | 0.277 | 5 | 11 | 1 | 5 | 8 |

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
| norm_negative|clean | 3258 | 3017 | 241 | 4 | 0.017 | 237 | 15 | 0.063 | 2 | 12 | 3 | 7 | 8 |
| norm_positive|clean | 1809 | 42 | 1767 | 11 | 0.006 | 1756 | 184 | 0.105 | 65 | 124 | 40 | 61 | 123 |

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
| gpt4o-claude46 | 4953 | 254 | 0.051 |
| gpt4o-deepseek_v4 | 4507 | 177 | 0.039 |
| claude46-deepseek_v4 | 4365 | 166 | 0.038 |

set tier0

| pair | n_families | n_differ | rate |
|---|---|---|---|
| gpt4o-claude46 | 1395 | 111 | 0.080 |
| gpt4o-deepseek_v4 | 1273 | 72 | 0.057 |
| claude46-deepseek_v4 | 1226 | 74 | 0.060 |

## Non-answer and p_x-missing counts per teacher (pool, screened families only)

| teacher | families not answered (either order) | answer rows without p_x |
|---|---|---|
| gpt4o | 16 | 0 |
| claude46 | 6 | 0 |
| deepseek_v4 | 1 | 0 |

## Exact order flips inside the band (pool)

band_exact_flip: logprob teacher with p_sym in [0.2, 0.8] and |p_o1 - p_o2| >= 0.9 (both orders confident, opposite). flip_only families are contested through such flips alone; the pre-registered sensitivity set is contested minus flip_only.

| teacher | answered | in band | exact flips | flip share |
|---|---|---|---|---|
| gpt4o | 5202 | 283 | 43 | 0.152 |
| claude46 | 5212 | 243 | 0 | 0.000 |
| deepseek_v4 | 5217 | 689 | 689 | 1.000 |

flip_only families: 440 of 1129 contested

## p_sym distribution (pool, answered families)

gpt4o

| bin | families |
|---|---|
| [0.00, 0.05) | 926 |
| [0.05, 0.20) | 89 |
| [0.20, 0.35) | 63 |
| [0.35, 0.50) | 73 |
| [0.50, 0.65) | 81 |
| [0.65, 0.80) | 66 |
| [0.80, 0.95) | 153 |
| [0.95, 1.00] | 3745 |

claude46

| bin | families |
|---|---|
| [0.00, 0.05) | 1106 |
| [0.05, 0.20) | 0 |
| [0.20, 0.35) | 0 |
| [0.35, 0.50) | 0 |
| [0.50, 0.65) | 243 |
| [0.65, 0.80) | 0 |
| [0.80, 0.95) | 0 |
| [0.95, 1.00] | 3847 |

deepseek_v4

| bin | families |
|---|---|
| [0.00, 0.05) | 873 |
| [0.05, 0.20) | 0 |
| [0.20, 0.35) | 0 |
| [0.35, 0.50) | 0 |
| [0.50, 0.65) | 689 |
| [0.65, 0.80) | 0 |
| [0.80, 0.95) | 0 |
| [0.95, 1.00] | 3634 |

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
| pool contested available | 1129 |
| pool contested chosen | 1129 |
| target | 1500 |
| written (E2c-C) | 1485 |
| flip_only among written | 553 |

E2c-C composition and the matched E2c-K draw (consensus pool incl. tier 0, seed 20261002):

| source | C chosen | K target | K drawn | K available |
|---|---|---|---|---|
| aita_berkeley | 15 | 15 | 15 | 35 |
| daily_dilemmas | 245 | 245 | 245 | 759 |
| hendrycks_ethics | 695 | 695 | 695 | 1205 |
| moral_stories | 199 | 199 | 199 | 1794 |
| moralchoice | 114 | 114 | 114 | 1025 |
| scruples | 217 | 217 | 217 | 362 |

K written: 1485 -> data/families/consensus_control_selected.jsonl
