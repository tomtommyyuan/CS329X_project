# E2c 转换人工抽检 第四轮（2026-10-05，仅 moral_stories：1 位修复 agent + 1 位判官 agent + 1 位盲审复核）

判定表 `data/annotation/e2c_handcheck_moral_stories.csv`（seed 20261008，100 行 = wave 1 50 + 2a 50，reserve 不入样；与前三轮已判的 300 个 moral_stories id 零重叠；第三轮判定表存档于 `data/annotation/e2c_handcheck_round3/`）。门：三列各 ≥ 90%。本轮前 Moral Stories 规则已按第三轮报告 (1)–(7) 修复并重建池（9,294 → 8,325 族；moral_stories 6,036 → 5,067，wave 1 600 → 493，2a 1,827 → 1,515；其余三源 + moralchoice 的 family_id / 文本 / wave / prompt 行逐字节不变）。

**结果：moral_stories 三列全部过门**（二人称 75 → 79 → 83 → **93**；两行动 99；情境无裁决 100；联合 92），且两个 wave 分别也都 ≥ 90。复核以 `numpy.default_rng(20261008)` 抽 25 行（wave 1 8 / 2a 17）盲判，三列与联合判定均 25/25 一致（复核判 3 个二人称失败、1 个行动失败，与判官逐行相同）。全表 pandas 重算：二人称 93/100、两行动 99/100、情境无裁决 100/100、联合 92/100；8 个 0 全带 note，`needs_review` 100 行全空，文本列与未判备份及重建后的池逐字节一致，csv QUOTE_ALL 重序列化逐字节一致；`.venv/bin/python -m pytest -q` 168 passed 1 skipped。

| 项 | 二人称 | 两行动互斥 | 情境无裁决 | 联合 |
|---|---|---|---|---|
| 全表 n=100 | **93** | 99 | 100 | 92 |
| wave 1 (n=50) | 47 (94%) | 50 | 50 | 47 |
| 2a (n=50) | 46 (92%) | 49 (98%) | 50 | 45 |
| 复核 25 行一致 | 25/25 | 25/25 | 25/25 | 25/25 |
| 第三轮 | 83 | 99 | 100 | 82 |
| 第二轮 | 79 | 96 | 100 | 76 |
| 第一轮 | 75 | — | — | — |

8 个失败全部 `needs_review` 为空，分为 6 个互不相关的小机制（判官报告 1–6），第一至三轮占主导的"角色名词引入他人 → 他人代词被过度替换"一类本轮只剩 1 行（ms_38F5OAUN，who 关系从句内）。

**判定：过门（PASS）。按 §10 退出规则，筛 moral_stories wave 1 + 2a；不再修第五轮。** 追加命令不变：`python scripts/17_contested_prompts.py --sources moral_stories --out data/prompts/contested_pool_T1_wave1_ms.jsonl`，再以同一 `--out` 跑 D。

论文须披露的残余缺陷类型（moral_stories 二人称转换，抽检点估计 7%，单侧 95% 上界约 12%）：

| 类型 | 抽检行数 | 例 |
|---|---|---|
| 行动者宾语 her/him 在副词 / 量词前被映为 "your"（无名词跟随） | 2 | ms_3NAPMVF0 "send your more information"；ms_3OLF68YT "supports your financially" |
| 源文分词 / 拼写噪声导致行动者引用残留 | 2 | ms_3FE7TXL1 "You 's friends"；ms_37UEWGM5 "Jakes sees a fight" |
| 他人代词在 who 关系从句并列内被替换为 you | 1 | ms_38F5OAUN "sells them to you" |
| 动名词主语致使句中行动者宾语 him 未转换 | 1 | ms_354GIDR5 "biking to work made him sweaty" |
| they 指 you + 他人（"each other" 未入组合短语表） | 1 | ms_31QNSG6A "they can disagree with each other" |
| 行动列：状态动词 want / be afraid 被命令式化，真实动作在 so 分句 | 1 | ms_39LNWE0K "Want to learn more ... but be afraid ..., so you choose" |
| 非失败但应提及：并列三单 / 过去时动词未还原（"and turns it up"、"and took"、"but doesn't have"）；源文噪声原样保留（"a tradesmen"、"go ahead an spend"、"turn of your phone"） | 7 + 7 | ms_3TR2532V、ms_3Z4GS9HP、ms_3QL2OFSM；ms_34X6J5FL |

另须披露：四轮规则收紧使 moral_stories 池从 10,989 源行缩到 5,067 族（46%），硬删以 `pronoun_same_gender_other`（5,195）与 `plural_refers_to_actor`（1,236）为主，故保留族偏向"情境中只出现行动者一人或他人为异性 / 复数"的故事；wave 1 从 600 缩到 493。

---

## 报告 1（修复 agent）

```
ROUND-4 FIX REPORT — E2c Moral Stories (no API calls; nothing committed)

1. Code: /Users/yuansir/workspace/CS329X_Project/src/vcd/data/load_contested_sources.py (Moral Stories path only; Reddit / ETHICS / MoralChoice code untouched)
- (1) Same-gender guard, name-list independent: `_person_pass` now tracks `others_seen` = genders of every role noun (new curated `_EXTRA_PERSON_N`, ~460 nouns incl. opponent / jock / roommate / waitress / patron / governor) and of ANY Title-cased non-actor token (`_is_name_token`; blocked after a determiner or inside a capital chain like "Kentucky Derby" / "Red Cross"; sentence-initial only if a known actor name or not a dictionary word). An actor-gender pronoun after a same- or unknown-gender other -> HARD `pronoun_same_gender_other`, never rewritten; also when the actor is not the certain clause subject and the preceding fields (situation for intention; situation+intention for actions) name such a person (`_RowCtx.row_others`). Not counted as others: "the governor of his state", "<Actor> is a 4th grader / an animal lover", "<Actor>, an accountant,", "husband Jeff" / "son, Aden" (name learns the role's gender, `_learn_name_genders`), generic anyone/everyone/nobody, "ex boyfriend" modifier. A single unknown-gender name takes the gender of the row's non-actor pronouns ("Penelope ... her"). Kept-object rule unchanged, but a kept object pronoun in a row that names nobody else -> HARD `pronoun_ambiguous` ("to keep him motivated").
- (2) `their` -> `your` only as determiner on an actor-relation noun with the actor as subject and no plural antecedent in the field or preceding context (`_relation_noun_after`, `_animate_plural_lemmas`); "their friend" no longer resets the subject via the verb "to friend".
- (3) `_UNAPOSTROPHISED` in `_ms_clean_field`: shes/hes/theyre/youre/im/ive/dont/doesnt/didnt/isnt/wasnt/arent/werent/cant/couldnt/wouldnt/shouldnt/hasnt/havent/hadnt/thats/whats/theres, case-insensitive.
- (4) "<Actor>'s found out" -> "You have found out" (`contraction_has`); `_possessive_without_noun` post-check -> HARD `possessive_without_noun` ("Your found", "your.", "yours back yard", "yours 3 dollar"); "back" removed from `_HIS_STANDALONE_NEXT`.
- (5) `_be_complement_is_adjectival` + `_ms_rescue_clause`: is/was + non-adjective (PP, determiner, passive participle), has/had, lives/feels/knows/owns/seems/remains... -> the "so" clause (then and/but/then) with the actor's eventive VBZ becomes the action (`stative_head_clause`), else HARD `action_stative_verb`. "Be honest / Be there for / Be very careful" stay.
- (6) `_group_phrase_follows`: they/their/them + "as a family / together / the two of you / both of you ..." with no plural before it in the clause -> `plural_refers_to_actor`.
- (7) `_verb_pass`: VBZ after and/then/but lemmatised when the preceding "subordinate clause" has no finite verb or 3sg subject (PPs like "after work", "until after dinner" via shared `_subord_is_clause`); relative who/which = clause subject; "and is/are" -> "be" in implicit-you imperatives; "you only has" -> have; "You, who live ... and wants" fixed; embedded "the food tastes wonderful and is" left alone (`_EMBEDDED_VBZ` whitelist); appositive ", Mia, gets" not lemmatised; coordination after singular collectives ("your family and talks") lemmatised.
- HARD_FLAGS += `possessive_without_noun`. New `_RowCtx` dataclass carries has_other / row_others / plurals per field.

2. Rebuild (scripts/16 with defaults, pinned waves; scripts/17 default)
- Moral Stories: loaded 10,989 -> 10,997 (rescued has-heads), rule-clean 6,038 -> 5,069, pool 6,036 -> 5,067; wave 1 600 -> 493, 2a 1,827 -> 1,515, reserve 3,609 -> 3,059 (incl. 131 newly clean families, all sent to reserve). Surviving families: 4,936, every one keeps its pinned meta.wave (0 changes); dropped 1,100. Pool total 9,294 -> 8,325. Prompts data/prompts/contested_pool_T1.jsonl 2,210 fam / 4,420 -> 2,103 / 4,206 (MS 493 / 986).
- Hard flags (Moral Stories, overlapping): pronoun_same_gender_other 5,195 (was 2,141; now also covers the role-noun cases formerly `pronoun_ambiguous` 2,324), plural_refers_to_actor 1,236 (1,234), possessive_without_noun 151 (new), pronoun_ambiguous 10 (new meaning: kept object pronoun with nobody else in the row), residual_actor_name 68, gender_unknown 41, actions_identical 1, reflexive_residual 1; auto edits in clean rows: stative_head_clause 76, singular_their 5, contraction_has 5.
- Round-3 judged failures (18): 14 dropped (13 pronoun_same_gender_other, one of them also plural_refers_to_actor; 1 pronoun_ambiguous = "keep him motivated"), 4 kept with corrected text (31EUONYN "You have found out ...", 3QAVNHZ3...MELAZ "join your coworkers", 3R2PKQ87 "Join a dating site for people your age.", 3OUYGIZW puppy borderline unchanged). Judged-pass rows retained: round 3 67/82, round 2 67/76, round 1 61/71 (losses are mostly rows where the other party's pronoun had been preserved by luck).
- Byte-identity proof (script in scratchpad, compared against `git show HEAD:` of both files): scruples 585, aita_berkeley 50, hendrycks_ethics 1,948, moralchoice 675 -> same family_id sets, identical situation / action_x / action_y / meta.wave for every family, identical row order, identical prompt_id + full prompt rows in contested_pool_T1.jsonl (1,170 / 100 / 600 / 1,350). PROOF: PASS. Only `meta.leak_max_cosine` differs on 630 non-MS rows (max |delta| 0.0062) because the leakage TF-IDF is refit on the new pool; moralchoice rows are fully identical.
- Wave pinning implemented in scripts/16: `--pin-waves` (default `auto` = read the existing `--out` file; `''` to redraw); new families from Moral Stories / ETHICS go to reserve. Report shows "pinned to data/families/contested_pool.jsonl: 8194 surviving families keep their wave, 131 new families -> reserve".

3. Hand-check sheet
- Round-3 judged sheet archived byte-identical to /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_round3/e2c_handcheck_moral_stories.csv (100 rows).
- New /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_moral_stories.csv: 100 rows = wave 1 50 + 2a 50 (reserve excluded), seed 20261008, 0 overlap with the 300 ids judged in rounds 1-3, needs_review empty on all 100 rows, situation / actions / wave byte-identical to the rebuilt pool, pass / note columns empty. scripts/16 new options: `--handcheck-waves 1:50,2a:50` (per-wave stratification), `--handcheck-exclude` default now lists round1,round2,round3, `--handcheck-sources` default moral_stories, `--handcheck-seed` default 20261008.

4. Tests: tests/test_contested.py +4 tests (`test_round4_*`, built from the 16 round-3 failure source rows + 3 controls, plus negative controls: Kentucky Derby, governor of his state, Penelope/her house, predicate nouns, "Ted asks his sister ... with him", legitimate plurals, adjectival "Be ..." heads, subordinate clauses keeping their verbs) and a wave-pinning / stratified-sheet check in the CLI test; fixture M1 given an unambiguous actor gender. `.venv/bin/python -m pytest -q`: 168 passed, 1 skipped (was 164 + 1).

5. Docs: tasks/e2c_plan.md status line, §1 (row 1d, build table, hard-flag paragraph, hand-check paragraph), §8 row 1, §10 规则转换残留 row (round-4 rules (1)-(7) in one sentence + costs), §11 rows A / B / C / D; results/e2c/pool_report.md regenerated by scripts/16.

Untouched as required: data/teacher_e2c/, data/prompts/contested_pool_T1_wave1_noms.jsonl, data/prompts/contested_pool_T1_wave2b.jsonl, results/e2c/screen_report_*.md, results/e2c/ms_pilot_*, data/families/families.jsonl, data/prompts/{pilot,train,dev,test}_prompts_v2.jsonl, scripts/19_e2c_analysis.py, src/vcd/analysis/e2c_metrics.py, tests/test_e2c_metrics.py.

Modified / new files: src/vcd/data/load_contested_sources.py, scripts/16_build_contested_pool.py, tests/test_contested.py, data/families/contested_pool.jsonl, data/prompts/contested_pool_T1.jsonl, results/e2c/pool_report.md, data/annotation/e2c_handcheck_moral_stories.csv, data/annotation/e2c_handcheck_round3/e2c_handcheck_moral_stories.csv (new dir), tasks/e2c_plan.md.
```

## 报告 2（判官 agent）

```
JUDGE REPORT — source moral_stories, ROUND 4 (seed 20261008; 100/100 rows read and judged by hand; ambiguous rows verified against the original third-person text in the local HF snapshot of moral_stories_full.jsonl; no API calls; nothing committed)

Sheet saved in place: /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_moral_stories.csv (same 11 columns, same row order, csv QUOTE_ALL; family_id / source / wave / situation / action_x / action_y / needs_review byte-identical to the unjudged sheet, backup at /private/tmp/claude-501/-Users-yuansir-workspace-CS329X-Project/64062123-fa10-4af6-86b2-26906e1a925d/scratchpad/ms_r4_backup.csv; every 0 carries a note; "minor:" / "pass;" notes on 19 passes). No other file touched.

PASS RATES (gate: each column >= 90%)

| n | second_person | two_exclusive_actions | no_verdict_in_situation | joint |
|---|---|---|---|---|
| all 100 | **93** | 99 | 100 | 92 |
| wave 1 (n=50) | 47 (94%) | 50 | 50 | 47 |
| 2a (n=50) | 46 (92%) | 49 | 50 | 45 |
| round 3 (n=100) | 83 | 99 | 100 | 82 |
| rounds 1 / 2 | 75 / 79 | — / 96 | — / 100 | — / 76 |

GATE VERDICT: PASS — all three columns >= 90% overall (93 / 99 / 100) and also within each wave separately (94 / 100 / 100 and 92 / 98 / 100). needs_review is empty on all 100 rows, so none of the 8 failures is reachable by an existing flag.

POLICY (same strict rubric as rounds 1-3): any 3rd-person reference denoting the decision-maker = P2 0; they/their/them for you+someone = P2 0; other party's pronoun over-replaced by you/your/yourself = P2 0; garbled actor reference (round-2 "yours in-laws", round-3 "Your found out" precedents) = P2 0; single coordinated 3sg / past-tense slip, or a 3sg agreement slip after "you" with no pronoun residue = pass with "minor" note (round-1/2/3 precedent); stative head imperativised with the real action in the "so" clause = actions 0 (round-3 ms_3R2PKQ87 precedent); outcome narrated inside an action only = pass (rubric scores the situation).

FAILURE PATTERNS (second_person, 7 rows)
1. Garbled actor reference: actor OBJECT pronoun (her) mapped to "your" with no noun following — 2 rows: ms_3NAPMVF0ZXDUHA4T9J6B5U75T0727Y ("send your more information", source "send her"), ms_3OLF68YTNAZW16E34HX2Z43K5AYFA0 ("supports your financially", source "supports her"). The round-4 `possessive_without_noun` post-check did not fire because the next token is an adjective/adverb ("more", "financially") rather than a verb or punctuation. Fix: object her/him -> "you" (not "your") when followed by an adverb, a quantifier, or a determiner-less NP head; extend the post-check so "your" must be followed by a noun phrase head, not merely a word.
2. Garbled actor reference from source tokenisation — 2 rows: ms_3FE7TXL1LJL4NS985IFH5LO0YYV2Q8 ("You 's friends", source "David 's friends" with spaced apostrophe), ms_37UEWGM5HU6XA86CZT435SO025ZR1F ("Jakes sees a fight", source typo "Jakes" for the actor Jake). Fix: treat "<Actor> 's" as the possessive ("Your friends"); hard-flag a capitalised sentence-initial token that is the actor name + "s" (or edit distance 1) before a VBZ.
3. Over-replacement of the OTHER party's pronoun — 1 row: ms_38F5OAUN5OAYW07BS49ISYD7KOQH78 ("sells them to you", source "sells them to him" = the low-income family member introduced by the role noun "family member"). The kept-object rule did not apply inside a relative clause coordinated after "who could use the items and"; the same-gender guard missed it because the subject chain reset at "who".
4. Actor's 3rd-person pronoun left unconverted — 1 row: ms_354GIDR5ZC493P1V9XHO7R43OTR00W ("biking to work made him sweaty", gerund-subject causative with the actor as object; the past-tense source "James lived ... where he worked" was otherwise converted). Fix: in a situation with no other person named, an object him/her after a non-animate subject (gerund / it / abstract noun) is the actor -> "you".
5. They for actor+someone — 1 row: ms_31QNSG6A5SR53P6IP0FCFLK8FI578C ("while you don't agree with her opinions, they can disagree with each other" = you + aunt). The round-4 `_group_phrase_follows` guard covers "as a family / together / the two of you" but not "with each other"; add "each other / one another" to the group-phrase list.

FAILURE PATTERN (two_exclusive_actions, 1 row)
6. Stative head imperativised — ms_39LNWE0K4VU0Q6URBUKE22S6SBNIUN (Y "Want to learn more about history but be afraid it will be too boring, so you choose to watch the horror movie"; source "wants ... but is afraid ..., so he chooses"). `_be_complement_is_adjectival` treated "afraid" as an adjectival complement, so the `stative_head_clause` rescue did not move the head to the "so" clause; "want" + infinitive should also count as stative for the rescue.

INFORMATIONAL (passed, noted; not column failures)
- Coordinated verb slips, "minor": 7 rows — ms_3TR2532V ("and turns it up" / "and holds it up"), ms_3EO896NR ("and rants"), ms_3QIYRE09 ("and talks to it"), ms_3VZLGYJE ("and double checks"), ms_3FPRZHYE ("and is loud" should be "be"), ms_3Z4GS9HP (past-tense "and waited" / "and demanded"), ms_3QL2OFSM (situation "You see ... but doesn't have"). Down from 22 rows in round 3; the round-4 rule (7) clearly reached most PP-separated coordinations, the residue is past-tense sources and coordination after a long object NP.
- Source noise passed: ms_38F5OAUN ("a tradesmen"), ms_3DPNQGW4 ("husbands"), ms_3LUY3GC6 ("compliment on"), ms_34X6J5FL ("go ahead an spend", "go the mall"), ms_3BWI6RSP ("leaving dog alone"), ms_31Q0U3WY ("local's"), ms_3TXMY6UC ("disinterest").
- Outcome narrated inside an action only (passed per rubric): ms_31Q0U3WY ("Mike sees the app"), ms_3PH3VY7D ("which she reluctantly does").
- Correctly preserved other-party pronouns verified against source: ms_30LB5CDZ ("for yourself" = himself), ms_3LUY3GC6 ("Greet her ... she has done her hair"), ms_3DPNQGW4 ("from him"), ms_3AMW0RGH ("your family for their weekly dinners", antecedent = family), ms_32Q90QCQ (singular they for the student).

RECOMMENDATION: gate passed on all three columns, overall and per wave; proceed to screen Moral Stories wave 1 + 2a per tasks/e2c_plan.md §10 (python scripts/17_contested_prompts.py --sources moral_stories --out data/prompts/contested_pool_T1_wave1_ms.jsonl, then scripts/04 on the same --out). The 7% residual is five small, mutually independent mechanisms (above), none of them the role-noun over-replacement class that dominated rounds 1-3; if a round-5 patch is cheap, items 1 (object her -> "your" before adverb/quantifier) and 2 ("<Actor> 's", actor-name typo) are deterministic hard-flag candidates and together cover 4 of the 7 second-person failures, but they are not required to pass the gate.
```

## 报告 3（盲审复核）

```
VERIFIER REPORT — moral_stories ROUND 4 (sample: numpy.random.default_rng(20261008).choice(100, 25, replace=False); re-judged blind before reading the judge's columns; no API; nothing committed)
Sample sheet rows (0-based): 5 8 9 11 16 20 29 32 51 61 64 68 71 72 73 74 76 80 86 87 88 90 92 93 99
  (wave 1 8 / 2a 17)

AGREEMENT WITH JUDGE
- pass_second_person: 25/25 (verifier 0 on 3 rows: ms_354GIDR5 "biking to work made him sweaty" = actor's him unconverted; ms_3FE7TXL1 "You 's friends" = garbled actor possessive; ms_37UEWGM5 "Jakes sees a fight" = residual actor name — identical to the judge's three)
- pass_two_exclusive_actions: 25/25 (verifier 0 on 1 row: ms_39LNWE0K Y "Want to learn more about history but be afraid it will be too boring, so you choose to watch the horror movie" — stative heads imperativised, real action in the so-clause; same as judge, round-3 ms_3R2PKQ87 precedent)
- pass_no_verdict_in_situation: 25/25 (0 fails both sides)
- joint: 25/25 (21/25 pass both sides)
- Minor-only rows seen in the sample and passed by both: ms_354GIDR5 X "and took a sponge bath" (past-tense coordination, row already 0 for the pronoun), ms_3QL2OFSM "You see ... but doesn't have" (3sg agreement after you, no pronoun residue), ms_34X6J5FL "go ahead an spend" / "go the mall" (source noise), ms_3LUY3GC6 "compliment on" (source noise), ms_3FE7TXL1 "turn of your phone" (source noise).
- Correctly preserved other-party pronouns checked in the sample: ms_3PDJHANY (Milo: he / him / himself), ms_3LUY3GC6 (coworker: her / she), ms_3IXQG4FA...B3 (Ted: he), ms_3IXQG4FA...B9W (parents: them / they), ms_3ITXP059 (team: they), ms_3AMYWKA6 (cat: it).
- Out-of-sample spot check of the judge's other 4 failures (ms_38F5OAUN "sells them to you", ms_3NAPMVF0 "send your more information", ms_31QNSG6A "they can disagree with each other", ms_3OLF68YT "supports your financially"): all four confirmed as genuine second-person failures under the rubric.

FULL-SHEET RECOMPUTATION (pandas, dtype=str)
- pass_second_person 93/100; pass_two_exclusive_actions 99/100; pass_no_verdict_in_situation 100/100; joint 92/100
- by wave: 1 (n=50) 47/50/50 joint 47; 2a (n=50) 46/49/50 joint 45
- column values are only {0,1}; needs_review empty on 100/100 rows; every one of the 8 zeros carries a note
- family_id / source / wave / situation / action_x / action_y / needs_review byte-identical to the unjudged backup (ms_r4_backup.csv, whose pass columns are all empty) and to data/families/contested_pool.jsonl (0 mismatches on situation / action_x / action_y / meta.wave); 0 overlap with the 300 moral_stories ids judged in rounds 1-3; re-serialising with csv.QUOTE_ALL reproduces the file byte-for-byte
- .venv/bin/python -m pytest -q: 168 passed, 1 skipped

GATE VERDICT: PASS — pass_second_person 93% >= 90%, pass_two_exclusive_actions 99%, pass_no_verdict_in_situation 100%, each also >= 90% within wave 1 (94 / 100 / 100) and within 2a (92 / 98 / 100). Trend 75 -> 79 -> 83 -> 93. The round-1..3 dominant mechanism (role-noun other party, actor-gender pronoun over-replaced) accounts for 1 of the 7 second-person failures; the rest are 5 independent small mechanisms, none reachable by an existing flag.

RECOMMENDATION (binary per the §10 exit rule): PASS -> the orchestrator screens moral_stories wave 1 + 2a (python scripts/17_contested_prompts.py --sources moral_stories --out data/prompts/contested_pool_T1_wave1_ms.jsonl, then scripts/04 on the same --out). No round 5.

RESIDUAL DEFECT TYPES TO DISCLOSE IN THE PAPER (moral_stories second-person conversion; hand-check point estimate 7%, one-sided 95% upper bound ~12% at n=100; two_exclusive_actions 1%)
1. Actor object pronoun her/him mapped to "your" before an adverb / quantifier with no noun following ("send your more information", "supports your financially") — 2/100.
2. Source tokenisation / spelling noise leaving the actor in third person ("You 's friends" from "David 's", "Jakes sees" from the typo "Jakes") — 2/100.
3. Other party's pronoun over-replaced by "you" inside a coordinated who-relative clause ("sells them to you") — 1/100.
4. Actor object pronoun unconverted after a gerund / inanimate subject ("biking to work made him sweaty") — 1/100.
5. "they" denoting you + the other party before "each other" ("they can disagree with each other") — 1/100.
6. Actions column: stative head "want ... but be afraid ..." imperativised with the real action in the so-clause — 1/100.
7. Non-failing but visible: coordinated 3sg / past-tense verbs not lemmatised after the imperative head ("and turns it up", "and took", "but doesn't have") in ~7/100 rows; source typos preserved verbatim ("a tradesmen", "go ahead an spend", "turn of your phone") in ~7/100 rows.
8. Selection bias from four rounds of hard drops: moral_stories kept 5,067 of 10,989 source rows (46%); the dominant drops (pronoun_same_gender_other 5,195, plural_refers_to_actor 1,236) remove stories where another same-/unknown-gender person or a group including the actor is mentioned, so the retained set over-represents single-actor and opposite-gender-other situations; wave 1 shrank 600 -> 493.
```
