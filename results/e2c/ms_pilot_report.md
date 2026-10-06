# E2c screening report

rule: contested = majorities differ between >= 2 teachers OR any logprob teacher p_sym in [0.2, 0.8]; Claude order split = contested; any non-answer -> excluded; families without a T1 prompt in --prompts = not_screened. teachers ['gpt4o', 'claude46', 'deepseek_v4']. excluded waves: none (0 families kept out of C and K).

bookkeeping (pool): {'families_without_any_demo': 0, 'families_not_screened': 0, 'readouts': "{'gpt4o': 'logprobs', 'claude46': 'sampling', 'deepseek_v4': 'logprobs'}"}

## Contested rate per set and source

| source | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| moral_stories | 82 | 0 | 82 | 0 | 0.000 | 82 | 5 | 0.061 | 4 | 3 | 0 | 1 | 4 |

### set pool: by source

| source | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| moral_stories | 82 | 0 | 82 | 0 | 0.000 | 82 | 5 | 0.061 | 4 | 3 | 0 | 1 | 4 |

## Per wave (pool)

| wave | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 9 | 0 | 9 | 0 | 0.000 | 9 | 1 | 0.111 | 1 | 1 | 0 | 0 | 1 |
| 2a | 22 | 0 | 22 | 0 | 0.000 | 22 | 2 | 0.091 | 2 | 1 | 0 | 0 | 2 |
| reserve | 51 | 0 | 51 | 0 | 0.000 | 51 | 2 | 0.039 | 1 | 1 | 0 | 1 | 1 |

## Per human / construction prior

### moral_stories

| prior | n | not_screened | screened | non_answer | non_answer_rate | answered | contested | contested_rate | majority_differ | uncertain_band | claude_order_split | flip_only | contested_excl_flip_only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| norm_negative|clean | 54 | 0 | 54 | 0 | 0.000 | 54 | 2 | 0.037 | 1 | 1 | 0 | 1 | 1 |
| norm_positive|clean | 28 | 0 | 28 | 0 | 0.000 | 28 | 3 | 0.107 | 3 | 2 | 0 | 0 | 3 |

## Teacher pairwise disagreement (defined majorities, both answered)

set pool

| pair | n_families | n_differ | rate |
|---|---|---|---|
| gpt4o-claude46 | 82 | 3 | 0.037 |
| gpt4o-deepseek_v4 | 81 | 3 | 0.037 |
| claude46-deepseek_v4 | 81 | 2 | 0.025 |

## Non-answer and p_x-missing counts per teacher (pool, screened families only)

| teacher | families not answered (either order) | answer rows without p_x |
|---|---|---|
| gpt4o | 0 | 0 |
| claude46 | 0 | 0 |
| deepseek_v4 | 0 | 0 |

## Exact order flips inside the band (pool)

band_exact_flip: logprob teacher with p_sym in [0.2, 0.8] and |p_o1 - p_o2| >= 0.9 (both orders confident, opposite). flip_only families are contested through such flips alone; the pre-registered sensitivity set is contested minus flip_only.

| teacher | answered | in band | exact flips | flip share |
|---|---|---|---|---|
| gpt4o | 82 | 2 | 0 | 0.000 |
| claude46 | 82 | 0 | 0 | nan |
| deepseek_v4 | 82 | 1 | 1 | 1.000 |

flip_only families: 1 of 5 contested

## p_sym distribution (pool, answered families)

gpt4o

| bin | families |
|---|---|
| [0.00, 0.05) | 0 |
| [0.05, 0.20) | 0 |
| [0.20, 0.35) | 0 |
| [0.35, 0.50) | 1 |
| [0.50, 0.65) | 1 |
| [0.65, 0.80) | 0 |
| [0.80, 0.95) | 1 |
| [0.95, 1.00] | 79 |

claude46

| bin | families |
|---|---|
| [0.00, 0.05) | 2 |
| [0.05, 0.20) | 0 |
| [0.20, 0.35) | 0 |
| [0.35, 0.50) | 0 |
| [0.50, 0.65) | 0 |
| [0.65, 0.80) | 0 |
| [0.80, 0.95) | 0 |
| [0.95, 1.00] | 80 |

deepseek_v4

| bin | families |
|---|---|
| [0.00, 0.05) | 4 |
| [0.05, 0.20) | 0 |
| [0.20, 0.35) | 0 |
| [0.35, 0.50) | 0 |
| [0.50, 0.65) | 1 |
| [0.65, 0.80) | 0 |
| [0.80, 0.95) | 0 |
| [0.95, 1.00] | 77 |

## Selection

| set | families |
|---|---|
| tier0 contested (all) | 0 |
| pool contested available | 5 |
| pool contested chosen | 5 |
| target | 100000 |
| written (E2c-C) | 5 |
| flip_only among written | 1 |

E2c-C composition and the matched E2c-K draw (consensus pool incl. tier 0, seed 20261002):

| source | C chosen | K target | K drawn | K available |
|---|---|---|---|---|
| moral_stories | 5 | 5 | 5 | 77 |

K written: 5 (not written; pass --consensus-select-out)
