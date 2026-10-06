# E2c contested pool report

existing families checked: 2936 (all splits); pool written: 8325 -> `data/families/contested_pool.jsonl`

## Per source

| source | loaded | rule-clean | leak drops | pool dups | kept |
|---|---|---|---|---|---|
| mc_low | 676 | 676 | 0 | 1 | 675 |
| scruples | 3195 | 585 | 0 | 0 | 585 |
| aita_berkeley | 539 | 50 | 0 | 0 | 50 |
| moral_stories | 10997 | 5069 | 0 | 2 | 5067 |
| ethics_justice | 2749 | 1948 | 0 | 0 | 1948 |

## Waves

pinned to `data/families/contested_pool.jsonl`: 8194 surviving families keep their wave, 131 new families -> reserve

| source | wave | families |
|---|---|---|
| aita_berkeley | 1 | 50 |
| hendrycks_ethics | 1 | 300 |
| hendrycks_ethics | 2b | 1600 |
| hendrycks_ethics | reserve | 48 |
| moral_stories | 1 | 493 |
| moral_stories | 2a | 1515 |
| moral_stories | reserve | 3059 |
| moralchoice | 1 | 675 |
| scruples | 1 | 585 |

## Hard flags (rows dropped before the pool)

| source | flag | rows |
|---|---|---|
| scruples | action_first_word_not_verb | 11 |
| scruples | action_missing | 106 |
| scruples | action_stative_verb | 139 |
| scruples | body_too_long | 1133 |
| scruples | body_too_short | 96 |
| scruples | bystander_post | 14 |
| scruples | long_action | 44 |
| scruples | not_second_person | 89 |
| scruples | opens_mid_stream | 69 |
| scruples | pronoun_residue | 4 |
| scruples | quoted_first_person | 429 |
| scruples | residual_first_person | 1 |
| scruples | residual_first_person_plural | 2254 |
| aita_berkeley | action_stative_verb | 16 |
| aita_berkeley | body_too_long | 294 |
| aita_berkeley | body_too_short | 10 |
| aita_berkeley | long_action | 7 |
| aita_berkeley | not_second_person | 10 |
| aita_berkeley | opens_mid_stream | 4 |
| aita_berkeley | quoted_first_person | 71 |
| aita_berkeley | residual_first_person | 1 |
| aita_berkeley | residual_first_person_plural | 446 |
| moral_stories | actions_identical | 1 |
| moral_stories | gender_unknown | 41 |
| moral_stories | plural_refers_to_actor | 1236 |
| moral_stories | possessive_without_noun | 151 |
| moral_stories | pronoun_ambiguous | 10 |
| moral_stories | pronoun_same_gender_other | 5195 |
| moral_stories | reflexive_residual | 1 |
| moral_stories | residual_actor_name | 68 |
| ethics_justice | action_first_word_not_verb | 35 |
| ethics_justice | action_stative_verb | 80 |
| ethics_justice | habit_discontinued | 575 |
| ethics_justice | residual_first_person_plural | 147 |

## All review flags among loaded rows (informational flags stay in needs_review)

| source | flag | rows |
|---|---|---|
| aita_berkeley | meta_sentence_removed | 453 |
| aita_berkeley | residual_first_person_plural | 446 |
| aita_berkeley | body_too_long | 294 |
| aita_berkeley | age_tag_removed | 245 |
| aita_berkeley | source_has_second_person | 101 |
| aita_berkeley | inner_question | 95 |
| aita_berkeley | quoted_first_person | 71 |
| aita_berkeley | leading_sentence_removed | 49 |
| aita_berkeley | action_plural_to_second | 36 |
| aita_berkeley | action_stative_verb | 16 |
| aita_berkeley | degerund_coordinated | 11 |
| aita_berkeley | body_too_short | 10 |
| aita_berkeley | not_second_person | 10 |
| aita_berkeley | long_action | 7 |
| aita_berkeley | leading_adverb_dropped | 7 |
| aita_berkeley | opens_mid_stream | 4 |
| aita_berkeley | head_verb_unknown | 2 |
| aita_berkeley | residual_first_person | 1 |
| hendrycks_ethics | habit_discontinued | 575 |
| hendrycks_ethics | habitual_adverbial_dropped | 464 |
| hendrycks_ethics | residual_first_person_plural | 147 |
| hendrycks_ethics | action_stative_verb | 80 |
| hendrycks_ethics | action_first_word_not_verb | 35 |
| hendrycks_ethics | head_verb_unknown | 7 |
| hendrycks_ethics | leading_pronoun_dropped | 2 |
| moral_stories | pronoun_same_gender_other | 5195 |
| moral_stories | plural_refers_to_actor | 1236 |
| moral_stories | possessive_without_noun | 151 |
| moral_stories | residual_actor_name | 68 |
| moral_stories | gender_unknown | 41 |
| moral_stories | gender_from_row | 15 |
| moral_stories | pronoun_ambiguous | 10 |
| moral_stories | actions_identical | 1 |
| moral_stories | reflexive_residual | 1 |
| scruples | degerund | 3025 |
| scruples | meta_sentence_removed | 2580 |
| scruples | residual_first_person_plural | 2254 |
| scruples | body_too_long | 1133 |
| scruples | source_has_second_person | 664 |
| scruples | inner_question | 626 |
| scruples | leading_sentence_removed | 461 |
| scruples | quoted_first_person | 429 |
| scruples | age_tag_removed | 237 |
| scruples | action_stative_verb | 139 |
| scruples | action_plural_to_second | 134 |
| scruples | action_missing | 106 |
| scruples | degerund_coordinated | 99 |
| scruples | body_too_short | 96 |
| scruples | not_second_person | 89 |
| scruples | opens_mid_stream | 69 |
| scruples | leading_adverb_dropped | 45 |
| scruples | long_action | 44 |
| scruples | short_action | 15 |
| scruples | bystander_post | 14 |
| scruples | head_verb_unknown | 13 |
| scruples | action_first_word_not_verb | 11 |
| scruples | leading_pronoun_dropped | 8 |
| scruples | pronoun_residue | 4 |
| scruples | residual_first_person | 1 |

## Leakage vs existing families (situation cosine, char_wb 3-5 TF-IDF)

vectorizer fitted on: max over the joint space (existing + pool) and the reference space (existing only). re-used on purpose (same family_id, sanity split): 676; dropped: 0; review band [0.7, 0.9): 0; source-item conflicts: 0

| max cosine bin (vs all existing, re-used rows excluded) | pool rows |
|---|---|
| [0.0, 0.3) | 5081 |
| [0.3, 0.5) | 2488 |
| [0.5, 0.7) | 83 |
| [0.7, 0.8) | 0 |
| [0.8, 0.9) | 0 |
| [0.9, 1.0] | 0 |

### Leakage audit vs dev / test only

pool rows checked (before within-pool dedup): 8328; max situation cosine vs any dev / test family: 0.593; rows >= 0.7: 0; re-used sanity rows max: 0.593

| max cosine bin (vs dev / test) | pool rows |
|---|---|
| [0.0, 0.3) | 7455 |
| [0.3, 0.5) | 861 |
| [0.5, 0.7) | 12 |
| [0.7, 0.8) | 0 |
| [0.8, 0.9) | 0 |
| [0.9, 1.0] | 0 |

Top-10 pool rows by cosine to dev / test:

| pool | max cosine |
|---|---|
| mc_C_031 | 0.593 |
| ms_3Y5140Z9DYENY1MVU8LKSW57HC6PI6 | 0.592 |
| ms_3QEMNNSB2YXHKK2968QS1DY9SDW7DM | 0.583 |
| ms_386CSBG1O0KS5TS9SKRKVY5CFCSQ6R | 0.574 |
| ms_3ZGVPD4G6UF7LJ4CBTIQX19U5FRTZN | 0.569 |
| ms_3QECW5O0KIZ9E5KN45BA8X2Z260T5B | 0.533 |
| mc_C_1137 | 0.528 |
| bk_10vhwmx | 0.528 |
| mc_C_771 | 0.521 |
| ms_3KXIR214I5EXYNMA7L842INV36U42A | 0.511 |

Action pairs matching a dev / test pair at >= 0.9 (topic overlap, kept unless the situation is also >= 0.7): 2

| pool | dev/test | action cosine | situation cosine |
|---|---|---|---|
| bk_z4kw98 | dd_1862 | 0.984 | 0.180 |
| eth_j_5b206f11ba9f | dd_38530 | 0.933 | 0.328 |

Sensitivity of the 0.9 cut (hand probes on a test DD situation, 2026-10-05): dropping articles 0.997 and reordering sentences 0.966 are caught; a synonym swap 0.842, contractions + determiners 0.754 and a first-half truncation 0.739 are not (review band only). The check therefore catches near-verbatim copies; light paraphrases rely on the source-item disjointness (Reddit / Moral Stories / ETHICS vs GPT-4-generated DD and hand-written MC).

## Within-pool duplicates

situation >= 0.9: 3; AITA post-id / title: 0

| dropped | kept | cosine |
|---|---|---|
| mc_C_1177 | mc_C_347 | 0.918 |
| ms_3MH9DQ757XAMUFOWL6KBHQFQDZOUG2 | ms_3P4RDNWND64RCQJXZVG0V0JVB1WJIB | 0.944 |
| ms_3UWN2HHPUZ3CPUDEJ526S96ZS7ISN6 | ms_3R6BYFZZP8A8XJMWFRPGJCEI4HKXF5 | 0.951 |

## Hand-check samples (seed 20261008, rows judged in `data/annotation/e2c_handcheck_round1,data/annotation/e2c_handcheck_round2,data/annotation/e2c_handcheck_round3` excluded, sources `moral_stories`, waves `1:50,2a:50`, for the human pass of plan §11 B)

| file | rows |
|---|---|
| data/annotation/e2c_handcheck_moral_stories.csv | 100 |

## Licenses (meta.license)

| source | license |
|---|---|
| aita_berkeley | cc-by-nc-4.0 |
| hendrycks_ethics | mit |
| moral_stories | unspecified on HF card; upstream github.com/demelin/moral_stories (derived from Social Chemistry 101, CC BY-SA 4.0) |
| moralchoice | cc-by-4.0 |
| scruples | research-only (allenai/scruples upstream; tasksource mirror says apache-2.0) |
