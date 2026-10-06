# E2c contested pool report

existing families checked: 2936 (all splits); pool written: 14079 -> `data/families/contested_pool.jsonl`

## Per source

| source | loaded | rule-clean | leak drops | pool dups | kept |
|---|---|---|---|---|---|
| mc_low | 676 | 676 | 0 | 1 | 675 |
| scruples | 3195 | 1782 | 0 | 6 | 1776 |
| aita_berkeley | 2710 | 948 | 0 | 0 | 948 |
| moral_stories | 10986 | 8578 | 0 | 3 | 8575 |
| ethics_justice | 2749 | 2105 | 0 | 0 | 2105 |

## Waves

| source | wave | families |
|---|---|---|
| aita_berkeley | 1 | 221 |
| aita_berkeley | 1_gated | 527 |
| aita_berkeley | 1_pilot | 200 |
| hendrycks_ethics | 1 | 300 |
| hendrycks_ethics | 2b | 1600 |
| hendrycks_ethics | reserve | 205 |
| moral_stories | 1 | 600 |
| moral_stories | 2a | 2711 |
| moral_stories | reserve | 5264 |
| moralchoice | 1 | 675 |
| scruples | 1 | 1776 |

## Hard flags (rows dropped before the pool)

| source | flag | rows |
|---|---|---|
| scruples | action_missing | 106 |
| scruples | action_stative_verb | 136 |
| scruples | body_too_long | 1142 |
| scruples | body_too_short | 96 |
| scruples | long_action | 44 |
| scruples | not_second_person | 86 |
| scruples | pronoun_residue | 4 |
| aita_berkeley | action_stative_verb | 249 |
| aita_berkeley | body_too_long | 1541 |
| aita_berkeley | body_too_short | 44 |
| aita_berkeley | long_action | 47 |
| aita_berkeley | not_second_person | 43 |
| aita_berkeley | title_unparsed | 88 |
| moral_stories | gender_unknown | 40 |
| moral_stories | pronoun_ambiguous | 2323 |
| moral_stories | residual_actor_name | 67 |
| ethics_justice | action_first_word_not_verb | 1 |
| ethics_justice | action_stative_verb | 76 |
| ethics_justice | habit_discontinued | 575 |

## All review flags among loaded rows (informational flags stay in needs_review)

| source | flag | rows |
|---|---|---|
| aita_berkeley | first_person_plural | 2262 |
| aita_berkeley | meta_sentence_removed | 2112 |
| aita_berkeley | body_too_long | 1541 |
| aita_berkeley | age_tag_removed | 1239 |
| aita_berkeley | source_has_second_person | 867 |
| aita_berkeley | inner_question | 533 |
| aita_berkeley | action_stative_verb | 249 |
| aita_berkeley | action_plural_to_second | 223 |
| aita_berkeley | title_unparsed | 88 |
| aita_berkeley | long_action | 47 |
| aita_berkeley | title_first_word_not_gerund | 45 |
| aita_berkeley | body_too_short | 44 |
| aita_berkeley | not_second_person | 43 |
| aita_berkeley | leading_adverb_dropped | 40 |
| hendrycks_ethics | habit_discontinued | 575 |
| hendrycks_ethics | habitual_adverbial_dropped | 464 |
| hendrycks_ethics | action_stative_verb | 76 |
| hendrycks_ethics | action_first_word_not_verb | 1 |
| moral_stories | pronoun_ambiguous | 2323 |
| moral_stories | pronoun_same_gender_other | 2125 |
| moral_stories | residual_actor_name | 67 |
| moral_stories | gender_unknown | 40 |
| scruples | degerund | 3020 |
| scruples | meta_sentence_removed | 2515 |
| scruples | first_person_plural | 2271 |
| scruples | body_too_long | 1142 |
| scruples | source_has_second_person | 909 |
| scruples | inner_question | 644 |
| scruples | age_tag_removed | 237 |
| scruples | action_stative_verb | 136 |
| scruples | action_plural_to_second | 134 |
| scruples | action_missing | 106 |
| scruples | body_too_short | 96 |
| scruples | not_second_person | 86 |
| scruples | leading_adverb_dropped | 45 |
| scruples | long_action | 44 |
| scruples | short_action | 15 |
| scruples | pronoun_residue | 4 |

## Leakage vs existing families (situation cosine, char_wb 3-5 TF-IDF)

vectorizer fitted on: max over the joint space (existing + pool) and the reference space (existing only). re-used on purpose (same family_id, sanity split): 676; dropped: 0; review band [0.7, 0.9): 1; source-item conflicts: 0

| max cosine bin (vs all existing, re-used rows excluded) | pool rows |
|---|---|
| [0.0, 0.3) | 8850 |
| [0.3, 0.5) | 4416 |
| [0.5, 0.7) | 146 |
| [0.7, 0.8) | 1 |
| [0.8, 0.9) | 0 |
| [0.9, 1.0] | 0 |

### Leakage audit vs dev / test only

pool rows checked (before within-pool dedup): 14089; max situation cosine vs any dev / test family: 0.611; rows >= 0.7: 0; re-used sanity rows max: 0.593

| max cosine bin (vs dev / test) | pool rows |
|---|---|
| [0.0, 0.3) | 12554 |
| [0.3, 0.5) | 1514 |
| [0.5, 0.7) | 21 |
| [0.7, 0.8) | 0 |
| [0.8, 0.9) | 0 |
| [0.9, 1.0] | 0 |

Top-10 pool rows by cosine to dev / test:

| pool | max cosine |
|---|---|
| ms_3QEMNNSB2YXHKK2968QS1DY9SDW7DM | 0.611 |
| ms_3Y5140Z9DYENY1MVU8LKSW57HC6PI6 | 0.607 |
| mc_C_031 | 0.593 |
| ms_386CSBG1O0KS5TS9SKRKVY5CFCSQ6R | 0.591 |
| ms_3Z9WI9EOZ0MMRFEVBYYRW3ITQ7AHKW | 0.589 |
| ms_3ZGVPD4G6UF7LJ4CBTIQX19U5FRTZN | 0.569 |
| ms_3ND9UOO81L0F8BR2RXWSC65VUPEWLO | 0.547 |
| ms_3QECW5O0KIZ9E5KN45BA8X2Z260T5B | 0.546 |
| mc_C_771 | 0.539 |
| ms_39RP059MEIR7QQBCWI1BP57ZKDXMBF | 0.538 |

Action pairs matching a dev / test pair at >= 0.9 (topic overlap, kept unless the situation is also >= 0.7): 4

| pool | dev/test | action cosine | situation cosine |
|---|---|---|---|
| bk_z4kw98 | dd_1862 | 0.984 | 0.180 |
| eth_j_5b206f11ba9f | dd_38530 | 0.941 | 0.347 |
| scr_azzupq | dd_31247 | 0.935 | 0.123 |
| bk_11s8b0w | dd_38530 | 0.905 | 0.241 |

Sensitivity of the 0.9 cut (hand probes on a test DD situation, 2026-10-05): dropping articles 0.997 and reordering sentences 0.966 are caught; a synonym swap 0.842, contractions + determiners 0.754 and a first-half truncation 0.739 are not (review band only). The check therefore catches near-verbatim copies; light paraphrases rely on the source-item disjointness (Reddit / Moral Stories / ETHICS vs GPT-4-generated DD and hand-written MC).

Review pairs:

| pool | existing | cosine |
|---|---|---|
| ms_3M81GAB8A1HYB594OB8S6ER4S9ZBQK | dd_36819 | 0.700 |

## Within-pool duplicates

situation >= 0.9: 5; AITA post-id / title: 5

| dropped | kept | cosine |
|---|---|---|
| mc_C_1177 | mc_C_347 | 0.924 |
| scr_b9eiks | scr_b96ad8 | 0.963 |
| ms_3MH9DQ757XAMUFOWL6KBHQFQDZOUG2 | ms_3P4RDNWND64RCQJXZVG0V0JVB1WJIB | 0.947 |
| ms_3DR23U6WE6C9AODGF64DCR8CFXDET7 | ms_3TMSXRD2X7Y2I4NYYNE9SRWHWT61W4 | 0.953 |
| ms_3UWN2HHPUZ3CPUDEJ526S96ZS7ISN6 | ms_3R6BYFZZP8A8XJMWFRPGJCEI4HKXF5 | 0.954 |
| scr_arh80p | scr_a0irny | 1.000 |
| scr_aqfwr1 | scr_a1oi8m | 0.920 |
| scr_b9knx7 | scr_b4wvh3 | 1.000 |
| scr_b1pbzb | scr_a1oi8m | 0.995 |
| scr_ayjhh3 | scr_ba1m24 | 1.000 |

## Hand-check samples (seeded, for the human pass of plan §11 B)

| file | rows |
|---|---|
| data/annotation/e2c_handcheck_aita_berkeley.csv | 100 |
| data/annotation/e2c_handcheck_hendrycks_ethics.csv | 100 |
| data/annotation/e2c_handcheck_moral_stories.csv | 100 |
| data/annotation/e2c_handcheck_scruples.csv | 100 |

## Licenses (meta.license)

| source | license |
|---|---|
| aita_berkeley | cc-by-nc-4.0 |
| hendrycks_ethics | mit |
| moral_stories | unspecified on HF card; upstream github.com/demelin/moral_stories (derived from Social Chemistry 101, CC BY-SA 4.0) |
| moralchoice | cc-by-4.0 |
| scruples | research-only (allenai/scruples upstream; tasksource mirror says apache-2.0) |
