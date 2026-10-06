# E2c screening report

rule: contested = majorities differ between >= 2 teachers OR any logprob teacher p_sym in [0.2, 0.8]; Claude order split = contested; any non-answer -> excluded; families without a T1 prompt in --prompts = not_screened. teachers ['gpt4o', 'claude46', 'deepseek_v4']. excluded waves: none (0 families kept out of C and K).

bookkeeping (pool): {'pool_not_screened': 1}

bookkeeping (tier0): {'other_variant': 26874, 'families_without_any_demo': 0, 'families_not_screened': 0, 'readouts': "{'deepseek_v4': 'logprobs', 'gpt4o': 'logprobs', 'claude46': 'sampling'}"}

## Calibration: existing train (tier 0)

valid 1469, contested 356, consensus 1113, non-answer 24 (expected 1,469 / 356 / 1,113 / 24)

## Contested rate per set and source

| source | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| daily_dilemmas | 1010 | 0 | 1010 | 6 | 0.006 | 1004 | 245 | 0.244 | 95 | 170 | 57 | 84 | 161 |
| moralchoice | 483 | 0 | 483 | 18 | 0.037 | 465 | 111 | 0.239 | 59 | 72 | 17 | 29 | 82 |

### set tier0: by source

| source | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| daily_dilemmas | 1010 | 0 | 1010 | 6 | 0.006 | 1004 | 245 | 0.244 | 95 | 170 | 57 | 84 | 161 |
| moralchoice | 483 | 0 | 483 | 18 | 0.037 | 465 | 111 | 0.239 | 59 | 72 | 17 | 29 | 82 |

## Per human / construction prior

### daily_dilemmas

| prior | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| daily_dilemmas:high | 1010 | 0 | 1010 | 6 | 0.006 | 1004 | 245 | 0.244 | 95 | 170 | 57 | 84 | 161 |

### moralchoice

| prior | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| moralchoice:high | 483 | 0 | 483 | 18 | 0.037 | 465 | 111 | 0.239 | 59 | 72 | 17 | 29 | 82 |

## Teacher pairwise disagreement (defined majorities, both answered)

set tier0

| pair | n_families | n_differ | rate |
|---|---|---|---|
| gpt4o-claude46 | 1395 | 111 | 0.080 |
| gpt4o-deepseek_v4 | 1273 | 72 | 0.057 |
| claude46-deepseek_v4 | 1226 | 74 | 0.060 |

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
| pool contested available | 0 |
| pool contested chosen | 0 |
| target | 1500 |
| written (E2c-C) | 356 |
| flip_only among written | 113 |

E2c-C composition and the matched E2c-K draw (consensus pool incl. tier 0, seed 20261002):

| source | C chosen | K target | K drawn | K available |
|---|---|---|---|---|
| daily_dilemmas | 245 | 245 | 245 | 759 |
| moralchoice | 111 | 111 | 111 | 354 |

K written: 356 (not written; pass --consensus-select-out)
