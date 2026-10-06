# E2c 转换人工抽检 第三轮（2026-10-05，仅 moral_stories：1 位修复 agent + 1 位判官 agent + 1 位盲审复核）

判定表 `data/annotation/e2c_handcheck_moral_stories.csv`（seed 20261007，100 行，与第一、二轮已判的 200 个 moral_stories id 零重叠；第二轮四表存档于 `data/annotation/e2c_handcheck_round2/`）。门：三列各 ≥ 90%。本轮前 Moral Stories 规则已按第二轮报告修复并重建池（9,294 族；moral_stories 7,770 → 6,036）。

**结果：moral_stories 二人称列 83% 仍未过门**（第一轮 75 → 第二轮 79 → 第三轮 83）；两行动 99%、情境无裁决 100% 过。复核以 `numpy.default_rng(20261007)` 抽 25 行盲判，三列与联合判定均 25/25 一致（复核判 6 个二人称失败、1 个行动失败，与判官逐行相同）。全表 pandas 重算：二人称 83/100、两行动 99/100、情境无裁决 100/100、联合 82/100。

| 项 | 二人称 | 两行动互斥 | 情境无裁决 | 联合 |
|---|---|---|---|---|
| 全表 n=100 | **83** | 99 | 100 | 82 |
| wave 1 (n=9) | 9 | 9 | 9 | 9 |
| 2a (n=29) | 22 | 29 | 29 | 22 |
| reserve (n=62) | 52 | 61 | 62 | 51 |
| 复核 25 行一致 | 25/25 | 25/25 | 25/25 | 25/25 |
| 第二轮 | 79 | 96 | 100 | 76 |

17 个二人称失败全部 `needs_review` 为空，即现有软 / 硬 flag 一个都碰不到；放宽 3 个边界行也只到 86%。分型：他人代词被过度替换为 you/your/yourself 10 行（他人由角色名词或无性别词条的名字引入，`pronoun_same_gender_other` 的同性别判断依赖性别词典，因此不触发；保留宾语 him/her 的规则不覆盖属格、that/if 从句主语与反身代词）；行动者第三人称残留 5 行（含源文用单数 they 指行动者 2 行、无撇号 "shes" 1 行）；they 指 you+他人 1 行；名字在主语位被映为 "Your" 1 行；行动列失败 1 行（状态动词 "is only around" 被命令式化）。另有 22 行 "and V-s" 并列三单未还原，按规则计过，但是最大的残余质量问题。

**判定：不过门。建议：再修一轮（第四轮），暂不筛 moral_stories wave 1，也不弃源。**

- 不现在筛：wave 1 的 9/9 只是 n=9（单侧 95% 下界约 72%），全表 17% 的代词缺陷会直接进入 teacher demo 并被学生学到；600 族 × 2 × 3 teacher = 3,600 次 ≈ $5 的花费不大，但筛出来的 contested 集合要是事后再剔除就要重跑 D–E，并且违反 §5 "冻结前不动池" 的顺序。
- 不弃源：moral_stories 是 2a 正向 norm 的唯一来源（1,827 + reserve 3,609），弃掉后 §1 的 1,500 目标只能靠 hendrycks 2b（1,600）补，题型会偏向单句 ethics 判断。
- 第四轮修法（对应判官报告 (1)–(7)，优先级排序）：(1) 同性别守卫改为与性别词典无关：任何角色名词或大写非行动者名字出现在同句 / 前一分句，而其后出现行动者性别的属格、that/if/whether/how 从句主语或 "for" 后反身代词，直接硬删（扩 `pronoun_same_gender_other`），不要再尝试改写；接受池再缩（估计 2a 再掉 20–30%，wave 1 600 仍可从 2a 补足）。(2) 单数 their 指行动者：行动者为分句主语且 their 修饰关系名词时映 your，否则硬标。(3) 无撇号缩写 shes/hes/theyre/youre 进缩写表。(4) 名字主语位 → You；加后检 "Your" 必接名词短语。(5) 状态动词主句（is around / has / is in）不命令式化，由 so/and then 分句承载动作，否则硬删。(6) 二人称主语后的 they + as a family / together → 硬标。(7) and/then/but 后紧接的 VBZ 一律还原，不论中间 PP 长度（质量项，不影响门）。
- 第四轮抽样改为按筛选顺序分层：wave 1 50 行 + 2a 50 行（reserve 不入筛选，不必再占样本），seed 另取，排除前三轮 300 个已判 id。
- 退出规则：第四轮二人称仍 < 90% 则弃 moral_stories 的 wave 1，缺口由 hendrycks 2b 与 scruples / moralchoice 补，并在 §10 记录题型偏置。
- 对已过门三源的 wave 1 筛选（`contested_pool_T1_wave1_noms.jsonl`，3,220 条）不受影响，继续。过门后追加命令不变：`python scripts/17_contested_prompts.py --sources moral_stories --out data/prompts/contested_pool_T1_wave1_ms.jsonl`（600 族 / 1,200 条），再以同一 `--out` 跑 D。

---

## 报告 1（修复 agent）

```
FIX AGENT REPORT — E2c moral_stories round-2 fixes (no API calls; tests 154 passed, 1 skipped)

1. Rule changes, `src/vcd/data/load_contested_sources.py` (Moral Stories block)
- HARD_FLAGS += `pronoun_same_gender_other`, `actions_identical` (x == y after stripping [..]/(..), lower-case, "xor"→"or" source-noise map), `reflexive_residual` ("Introduce himself …" = mis-inferred actor gender).
- Over-replacement (judge item 2): `_person_pass` tracks the clause subject (`subj`); when the actor is the certain subject (imperative head, actor name / converted he-she in subject position), an object `him`/`her` (direct object or after at/to/for/about/from/of/… but not with/next to/behind/in front of/around) is kept as "somebody else". Resets to the old behaviour on subordinators and wh-words, object-control infinitives ("ask your friend at work to", "a cab to pick him up", "for an ambulance to"), causatives ("make the bully stop", "help her lift"), new subjects (name/noun + aux/VBZ, it/they + verb, "the ticket written to him"), reduced relatives ("your friends inviting him", "a phone call asking him", "being read to her"), and for/of/into + gerund. Lower-cased other names ("tells max") count as names. Actor-as-appositive rewrite: "Jeff's friend Murray who has" → "you, Jeff's friend, who have".
- Plural (item 3): `_has_plural_antecedent` no longer treats VBZ homographs (needs, wants, hates) as plural nouns (this is why the in-action branch never fired); `they/their` need an animate antecedent (people/animal/group nouns, -ers/-ors…, "in-laws"; a gender-neutral singular licenses `their/them` only, with no he/she/name around); `them` any plural.
- Determiner his/her → `your` never `yours` ("your in-laws", "your last day", "out of your neighborhood"); standalone his/hers → yours only before punctuation/conjunction.
- he's/she's → `you're` by default, `you've` only before been/got/gotten/had; "<Name>'s V-ing" → "you are V-ing" unless a compound ("Elaine's connecting flight" → "Your").
- be + V-ing head → lemmatised ("Have a picnic", "Go to the park", "is going to tell" → "Tell"); adjectival -ing stays "Be controlling".
- Coordinated VBZ: lemmatised across nominal coordination ("the woman and breaks up" → "break up"), after a subordinate clause when a comma precedes or the embedded verb disagrees ("that were … and burns" → "burn"), noun/verb homographs decided by complement or by a preceding plural noun ("cat and dogs" kept; the old code produced "Feed the cat and dog"); "you has" → "you have", "You, who lives/is …, is" → "live/are …, are", "you are doesn't" → "don't", "so you texts" → "text" (lemminflect-unknown verbs via `_EXTRA_VERBS`).

2. Tests: `tests/test_contested.py` +5 tests (`test_round2_*`), 125 lines, built from the judged source rows (ms_3U8YCDAG, ms_3M68NM07, ms_3VA45EW4, ms_3KXIR214, ms_35H6S234, ms_3W8CV64Q, ms_3SKEMFQB, ms_354P56DE, ms_3I2PTA7R, ms_38SKSKU7, ms_3WQ3B2KG, ms_379J5II4, ms_32RIADZI, ms_3M0NZ3JD, ms_39OWYR0E, ms_3BF51CHD, ms_3907X2AH, ms_39O5D9O8, ms_3300DTYQ, ms_3JC6VJ2S, ms_3K3R2QNK…) plus negative controls. `.venv/bin/python -m pytest -q`: 154 passed, 1 skipped.

3. Rebuild (`scripts/16_build_contested_pool.py --handcheck-sources moral_stories`, then `scripts/17_contested_prompts.py`)
- moral_stories: loaded 10,989; rule-clean 7,772 → 6,038; pool 7,770 → 6,036; wave 1 600 → 600 (300 pos / 300 neg); 2a 2,424 → 1,827; reserve 4,746 → 3,609.
- Hard flags (moral_stories, overlapping): pronoun_same_gender_other 2,141 (new hard), plural_refers_to_actor 1,050 → 1,234, pronoun_ambiguous 2,325 → 2,324, residual_actor_name 68, gender_unknown 40, actions_identical 1 (new), reflexive_residual 1 (new).
- Other sources unchanged: moralchoice 675, scruples 585, aita_berkeley 50, hendrycks_ethics 1,948 (300 / 2b 1,600 / 48). Pool total 11,028 → 9,294; leak drops 0; within-pool dups 3.
- `data/prompts/contested_pool_T1.jsonl`: 2,210 families / 4,420 T1 prompts (moral_stories 600 / 1,200), rewritten. `data/prompts/contested_pool_T1_wave1_noms.jsonl` and `data/teacher_e2c/` not touched.
- Of the 24 round-2 judged failures, 18 are now hard-dropped and 6 kept with corrected text; 72 of the 76 round-2 passes remain in the pool.

4. Hand-check sheet (round 3): `data/annotation/e2c_handcheck_moral_stories.csv`, 100 rows (wave 1 9 / 2a 29 / reserve 62), seed 20261007, 0 overlap with rounds 1–2 (200 judged moral_stories ids), `needs_review` empty on every row, text byte-identical to the pool. Round-2 judged sheets archived to `data/annotation/e2c_handcheck_round2/` (4 files); the three passing sources' sheets at `data/annotation/e2c_handcheck_{scruples,aita_berkeley,hendrycks_ethics}.csv` are unchanged. `scripts/16`: `--handcheck-exclude` accepts a comma list (default round1,round2), new `--handcheck-sources` (default all), default seed 20261007.

5. Docs: `tasks/e2c_plan.md` status line, §1 (row 1d, build table, hard-flag paragraph, hand-check paragraph), §2 within-pool row, §7 人工 row, §8 rows 1 and 3, §10 残留 row, §11 A/B/D updated; `results/e2c/pool_report.md` regenerated by scripts/16.

Known residual (not fixed, documented in tests as expected behaviour): sloppy sources where "him" should be "himself" ("to make him feel better"), coordination-attachment ambiguities ("and confronts him" after a that-clause), names that are never an actor elsewhere (e.g. "Sparky", "Jamal") still read as the actor's pronoun antecedent; single coordinated VBZ slips after an agreeing embedded verb remain ("until someone's food is put … and grabs it").

Files: /Users/yuansir/workspace/CS329X_Project/src/vcd/data/load_contested_sources.py, /Users/yuansir/workspace/CS329X_Project/tests/test_contested.py, /Users/yuansir/workspace/CS329X_Project/scripts/16_build_contested_pool.py, /Users/yuansir/workspace/CS329X_Project/data/families/contested_pool.jsonl, /Users/yuansir/workspace/CS329X_Project/data/prompts/contested_pool_T1.jsonl, /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_moral_stories.csv, /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_round2/, /Users/yuansir/workspace/CS329X_Project/results/e2c/pool_report.md, /Users/yuansir/workspace/CS329X_Project/tasks/e2c_plan.md. Nothing committed.
```

## 报告 2（判官 agent）

```
JUDGE REPORT — source moral_stories, ROUND 3 (seed 20261007; 100/100 rows read and judged by hand, no API)
Sheet saved in place: /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_moral_stories.csv (same 11 columns, same row order, csv QUOTE_ALL; situation/action/needs_review text byte-identical to the unjudged sheet; every 0 carries a note, "minor:"/"pass;" notes on 25 passes; unjudged backup at /private/tmp/claude-501/-Users-yuansir-workspace-CS329X-Project/64062123-fa10-4af6-86b2-26906e1a925d/scratchpad/ms_r3_backup.csv). No file other than the sheet was touched.

PASS RATES (gate: each column >= 90%)
- pass_second_person: 83/100 (round 2: 79, round 1: 75) -> FAILS gate
- pass_two_exclusive_actions: 99/100 (round 2: 96) -> passes
- pass_no_verdict_in_situation: 100/100 (round 2: 100) -> passes
- all three jointly: 82/100 (round 2: 76)
- by wave: wave 1 n=9: P2 9/9, joint 9/9; 2a n=29: P2 22/29, joint 22/29; reserve n=62: P2 52/62, joint 51/62
- needs_review is empty on all 100 rows, so none of the 17 P2 failures is reachable by any existing soft or hard flag.
- Policy sensitivity: 3 of the 17 P2 fails are borderline (ms_31EUONYN garbled "Your found out", ms_3OUYGIZW "his things" owner vs puppy, ms_3W8CV64Q...OMH9C "they ... as a family"); tolerating all three gives P2 = 86, joint = 85 — still under the gate.

POLICY (same strict rubric as rounds 1-2): any 3rd-person pronoun/possessive denoting the decision-maker in situation or action = P2 0; they/their/them for you+someone = P2 0; the other party's pronoun over-replaced by you/your/yourself = P2 0; garbled actor pronoun form = P2 0 (round-2 "yours in-laws" precedent); single coordinated 3sg slip (per action) = pass with "minor" note; non-imperative head or two actions that no longer describe one decision = actions 0; quoted first-person speech (ms_37Z929RL brownies quote, ms_3DYGAII7 riddle) = pass. No situation leaked a verdict or completed deed.

FAILURE PATTERNS (most common first)
1. Over-replacement of the OTHER party's pronoun by you/your/yourself — 10 rows (59% of P2 fails). In every case the other party is introduced by a role noun or by a name with no gender entry, so `last` never equals the actor's gender and `pronoun_same_gender_other` cannot fire; and the kept-object rule covers only object him/her, not possessive determiners, embedded-clause subjects or reflexives. Examples: ms_3H7Z272LX85PO2U1FBIXKCXZZTMPLX ("how cold your hands are" = Lloyd's; "ask Lloyd if you would like"; "you should have brought gloves ... you knew you were"), ms_3IAS3U3I0GEHJM7JM0IRAWT1E4FB24 ("exclaim that you look amazing" = Reina), ms_37Z929RLGA6AK7IYG1OI18CRI88TSF ("your daughter had done your homework"); also ms_3180JW2O (Emile's "your ideas"), ms_3E47SOBE (the jock's "your friends"), ms_3570Y55X ("work to beat you" = opponent), ms_3QAVNHZ3...E3LA8 ("get back to your ASAP" = sister), ms_3TXMY6UC (roommate's "your closet"), ms_354P56DE...R907SU ("ordered for yourself" = best friend), ms_3Z4AIRP3 ("Kate invites you to your party").
2. Actor's 3rd-person pronoun left unconverted — 5 rows: ms_3L2IS5HSFBGS475I8AX67AONC4CUNW ("to keep him motivated"), ms_3QRYMNZ7FZFD4UQT857W2E2LT44NTP ("tell your sister shes mad at her" — unapostrophised "shes" not in the contraction map), ms_3QAVNHZ3EN2I1YOZQS00UH840MELAZ ("Decide not to join their coworkers" — singular "their" for the actor); also ms_3A1PQ49W ("Tell their friend"), ms_3OUYGIZW ("peeing on all of his things", borderline). The two "their"-for-actor cases are a new sub-pattern: the source uses singular they for the actor, and the plural rule treats it as licensed by the gender-neutral other ("your friend ... their inhaler").
3. Plural they for actor+others — 1 row (borderline): ms_3W8CV64QJ3X2AJV471726U4DFOMH9C ("Cook something that they used to eat often as a family" — the family includes you). The round-2 "they drive there" type did not recur.
4. Garbled actor reference — 1 row: ms_31EUONYN2W1AZ7UUEF7OILQBH3FVOR ("Your found out your girlfriend died" — actor name mapped to "Your" in subject position).
5. Action pair broken — 1 row (actions 0): ms_3R2PKQ87NX6HDYPI2STSBSBCDKNIMM ("Be only around young girls all day, so you join a dating site for people your age" — stative "is only around" imperativised; the real action is in the subordinate clause).

INFORMATIONAL (passed, noted; not column failures)
- Single coordinated/appositive 3sg slips, "minor": 22 rows, e.g. ms_3VW04L3Z ("and brings flowers"), ms_3K772S5N ("but has to take care"), ms_3NG53N1R ("You, who only has ... gets"; "you only has" — 3 slips, no pronoun residue), ms_3Y4W8Q93 (one slip in each action: "takes it", "has plenty"), ms_3R3YRB5G ("and splitting" gerund not lemmatised). The fix report's coordinated-VBZ lemmatisation reaches the imperative head but still misses many "and V-s" continuations; this is the largest residual quality issue although it does not fail the rubric.
- Imperativised "and are ..." (should be "be"): ms_38F71OA9 ("Act up and are disruptive"), ms_3Z7VU45I ("and are completely open").
- Source noise passed: ms_324G5B4F ("and avid" for "an"), ms_31EUONYN ("hill yourself"), ms_3300DTYQ...X87EQO ("making sure it understands" for the child), ms_3Y5140Z9 (delivery driver only in actions), ms_3EG49X35...L6XT (outcome narrated inside action_y only).

REMAINING CONVERSION BUGS / RULE FIXES
- (1) The same-gender guard must not depend on a known-gender name list. Treat any other person introduced by a role noun (daughter, sister, roommate, best friend, opponent, jock, classmate, waitress, mother ...) or by ANY capitalised non-actor name as a potential same-gender antecedent; when such a mention precedes an actor-gender pronoun in the same sentence (or the previous clause) and the pronoun is a possessive determiner, an embedded-clause subject after that/if/whether/how, or a reflexive after "for", hard-drop (extend `pronoun_same_gender_other`) unless the actor is the certain subject AND the pronoun is in subject position. 10/17 P2 fails are this.
- (2) Singular "their/them" denoting the actor ("their coworkers", "Tell their friend"): when "their" is a determiner on a noun that is the actor's relation (coworkers/friend/boss/...) and the actor is the subject of that clause, map to "your"; otherwise hard-flag.
- (3) Add unapostrophised contractions shes/hes/theyre/youre to the contraction map ("shes mad at her").
- (4) Name-in-subject-position -> "You", never "Your" ("Your found out"); add a post-check that "Your" is always followed by a noun phrase.
- (5) Stative heads (is only around / is around / has / is in) must not be imperativised; when the main clause is stative and a "so/and then" clause carries the eventive verb, imperativise that clause or hard-drop.
- (6) they + "as a family / together / the two of you" after a second-person subject = actor+others: hard-flag.
- (7) Coordinated VBZ after a direct object or adverbial ("Go to the cemetery after work and brings", "Wait until after dinner then talks") is still not lemmatised in ~22% of rows; lemmatise any VBZ immediately after and/then/but whose preceding clause head is the imperative, regardless of intervening PP length.
```

## 报告 3（盲审复核）

```
VERIFIER REPORT — moral_stories ROUND 3 (sample: numpy.random.default_rng(20261007).choice(100, 25, replace=False); re-judged blind before reading the judge's columns; no API)
Sample sheet rows (0-based): 6 9 15 16 20 22 24 28 34 37 40 41 44 48 50 56 57 70 75 76 77 80 81 83 99
  (wave 1 0 / 2a 9 / reserve 16)

AGREEMENT WITH JUDGE
- pass_second_person: 25/25 (verifier 0 on 6 rows: ms_3180JW2O "shout down your ideas" = Emile's; ms_3E47SOBE "come with your friends" = the jock's; ms_3TXMY6UC "shirt in your closet" = roommate's; ms_3H7Z272L "how cold your hands are" / "ask Lloyd if you would like" = Lloyd; ms_3IAS3U3I "exclaim that you look amazing" = Reina; ms_3Z4AIRP3 "Kate invites you to your party" = Kate's — identical to the judge's six)
- pass_two_exclusive_actions: 25/25 (verifier 0 on 1 row: ms_3R2PKQ87 "Be only around young girls all day, so you join a dating site" — stative head imperativised; same as judge)
- pass_no_verdict_in_situation: 25/25 (0 fails both sides; ms_3EG49X35 outcome narrated inside action_y only, passed by both as the rubric scores the situation)
- joint: 25/25 (18/25 pass both sides)
- Minor-only rows seen in the sample and passed by both: ms_31QTRG6Q "and pays the bill", ms_3KB8R4ZV "proceeds to open", ms_3K772S5N "but has to take care", ms_3JAOYWH7 "and later sees", ms_324G5B4F "and avid" (source noise).

FULL-SHEET RECOMPUTATION (pandas, dtype=str)
- pass_second_person 83/100; pass_two_exclusive_actions 99/100; pass_no_verdict_in_situation 100/100; joint 82/100
- by wave: 1 (n=9) 9/9/9 joint 9; 2a (n=29) 22/29/29 joint 22; reserve (n=62) 52/61/62 joint 51
- needs_review empty on 100/100 rows; every 0 carries a note; situation/action_x/action_y/needs_review byte-identical to the unjudged backup (ms_r3_backup.csv)

GATE VERDICT: FAIL — pass_second_person 83% < 90% (two_exclusive_actions 99% and no_verdict 100% pass). Trend 75 -> 79 -> 83 over three rounds; 10/17 failures share one mechanism (other party introduced by role noun / unknown-gender name, actor-gender pronoun over-replaced) that no current flag reaches.

RECOMMENDATION: fix again (round 4); do not screen moral_stories wave 1 now; do not drop the source.
- Not now: wave 1 9/9 is n=9 (one-sided 95% lower bound ~72%); a 17% pronoun-defect rate would enter teacher demos and the SFT set; re-screening after a later fix would redo D-E for this source. The cost itself is small (600 x 2 x 3 = 3,600 calls, ~$5).
- Not drop: moral_stories is the only 2a positive-norm source (1,827 + reserve 3,609); without it the 1,500 target leans on hendrycks 2b (1,600) and the item mix shifts to single-sentence ethics judgements.
- Round 4: implement judge items (1)-(6) with (1) as a name-list-independent HARD drop (not a rewrite) and accept further pool shrinkage; (7) is quality-only. Sample 50 wave 1 + 50 2a (reserve is not screened) with a new seed, excluding the 300 judged ids. Exit rule: if round 4 second_person is still < 90%, drop moral_stories from wave 1, fill from hendrycks 2b / scruples / moralchoice, and record the item-type bias in e2c_plan §10.
- The running screen on contested_pool_T1_wave1_noms.jsonl (3,220 prompts, three passing sources + moralchoice) is unaffected. On a pass: python scripts/17_contested_prompts.py --sources moral_stories --out data/prompts/contested_pool_T1_wave1_ms.jsonl (600 families / 1,200 T1 prompts), then scripts/04 with the same --out files to append.
```
