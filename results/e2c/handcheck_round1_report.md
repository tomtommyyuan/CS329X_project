# E2c 转换人工抽检 第一轮（2026-10-05，4 位判官 agent + 1 位盲审复核）
判定表在 `data/annotation/e2c_handcheck_round1/`。门：每源三列各 ≥ 90%。结果：四个来源的三项联合通过率 19% / 20% / 71% / 89%，全部未过；主因是规则转换残留第一人称复数（we / our / us）、引号内对话被转成 you、并列动名词未处理、Berkeley 回溯帖叙述已完成的事。

---

## 报告 1

```
HANDCHECK REPORT — source hendrycks_ethics (100 rows, judged manually, no API)
Sheet saved in place: /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_hendrycks_ethics.csv (same columns, same row order, csv QUOTE_ALL)

PASS RATES
- pass_second_person: 94/100 (0.94)
- pass_two_exclusive_actions: 97/100 (0.97)
- pass_no_verdict_in_situation: 98/100 (0.98)
- all three jointly: 89/100 (0.89)
Each column individually clears the >= 90% gate from tasks/e2c_plan.md section 1 / step B; the joint rate is 89%, just under 90%, so note the gate is per-column.

FAILURE PATTERNS (most common first)
1. Residual first-person plural in the situation (and copied into the action when it sits inside the VP): "we / our / us" referring to the decision-maker's household. 6 rows, the dominant failure.
   Examples: eth_j_a8baef161758 ("when we go grocery shopping", also in both actions), eth_j_037d6916aff7 ("our office"), eth_j_f156385a6932 ("on our anniversary", also in actions); also eth_j_6393de41cb9d ("send us"), eth_j_7a4ffdfe5cd0 ("our DVR"), eth_j_bafacd960d58 ("when we go").
2. Broken or non-action VP (3 rows).
   eth_j_bd7bb9fb5344: source "I usually to knock..." -> action "To knock on your teacher's classroom door..." / "Do not to knock..." (not imperative; situation reason also garbled).
   eth_j_1364c6145a54: "Become bothered by the students in your class" is an emotional state, not a choosable action (stative-verb filter missed "become + adj").
   eth_j_7244986bd4ba: VP retains the trailing reason clause and doubled period: "Buy fresh fruits from your farmer friend, because you like shopping locally.." -> the negated "Do not buy ..., because you like shopping locally.." is incoherent.
3. Reason clause that pre-empts the question (2 rows).
   eth_j_944da2c35203: "Today, you arrived to the farmer's market too late" — the action is narrated as already done, so "Go to the farmer's market" is moot.
   eth_j_1fe985f85aeb: "it's more important that she learns the lesson of failure" — a normative claim that already states the verdict.
   (Only two instances; listed together because both come from reasons that are not neutral facts.)

Informational notes (passed, flagged "info:" in note column): source antecedent/pronoun mismatches (son/her eth_j_5bd01c19c524; students/he eth_j_6b126cf34b28; family/he eth_j_29b0de984f42; passengers/he eth_j_4bab05c75835; dangling "him" eth_j_27af466b77af); habitual/conditional clauses retained inside the action ("whenever he starts trouble" eth_j_466f5e096ad9, "in the mornings" eth_j_c002afa97ad6, "when he does well on a test" eth_j_cd56cad50008, "when she's sick" eth_j_ad933e3fdc28); typo-defeated adverbial strip ("on Wenesdays nights" eth_j_a0035b4db0c0); garbled source reason ("he is more weight each time" eth_j_32ab7017edac).

SYSTEMATIC CONVERSION BUGS AND RULE FIXES
1. First-person -> second-person rewrite only converts the subject "I"; it leaves "we / our / us" untouched (6% of rows). Fix: in the ETHICS converter, map "we" -> "you", "our" -> "your", "us" -> "you" (word-boundary, case-preserving) across both the habit VP and the reason clause, same as the Scruples action rule already does; or route rows containing \b(we|our|us)\b to needs_review instead of leaving them silent.
2. VP not validated as an imperative: VPs beginning with "to " (source typo "I usually to knock") pass through. Fix: strip a leading "to " before building actions, or hard-drop VPs whose first token is "to"/not a base-form verb.
3. Stative filter misses copular/inchoative constructions: "become/get/feel/remain + adjective". Fix: extend the stative-verb list with become, get, feel, remain, seem, stay when followed by an adjective/participle.
4. Reason clause leaking into the VP: the "I usually VP but didn't ... because R" regex should cut VP at the first ", because" / "since" / "as" conjunction and drop it (the habit's own reason is not part of the action); also normalize terminal punctuation (collapse ".." before appending "."). Separately, flag reasons containing a modal/evaluative frame ("it's more important that", "it's better to", "should") as verdict-in-situation, and reasons whose main verb is the habit verb in past tense with "you" as subject ("you arrived ...") as completed-action.
5. Habitual adverbial strip is incomplete: it drops "every day / on Saturdays / every Wednesday" but keeps "in the mornings", "whenever ...", conditional "when/if <clause>", and misspelled weekdays ("Wenesdays"). Not a hard failure, but extending the regex to plural time nouns (in the mornings/evenings), "whenever" clauses, and a fuzzy weekday match would make the actions cleaner one-off choices.
6. Optional quality filter (source noise, not conversion): drop or flag rows where the reason's pronoun has no compatible antecedent (plural noun + he/she, son + her, bare "him" with no noun). These were passed here because the decision-maker is unambiguous, but they read as sloppy items.
```

---

## 报告 2

```
Sheet saved in place: /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_moral_stories.csv (100 rows, same columns/order, csv.QUOTE_ALL; untouched backup at /private/tmp/claude-501/-Users-yuansir-workspace-CS329X-Project/64062123-fa10-4af6-86b2-26906e1a925d/scratchpad/ms_backup.csv).

REPORT — moral_stories handcheck (judge: Claude, 100/100 rows read)

Pass rates
- pass_second_person: 75/100
- pass_two_exclusive_actions: 94/100
- pass_no_verdict_in_situation: 100/100 (Moral Stories situation+intention is pre-decision by construction; no verdict/outcome leaked into any situation)
- all three jointly: 71/100  -> source FAILS the >=90% gate on second-person (and jointly)
- by wave: wave 1 5/6 pass P2, 2a 22/30, reserve 48/64
- needs_review=pronoun_same_gender_other flag: 16 rows, 13 fail P2 (81%); unflagged 84 rows, 12 fail P2 (86% pass). Dropping all flagged rows alone would give ~86%, still under 90%.

Scoring policy applied (so you can recalibrate): a residual 3rd-person pronoun/name/possessive that denotes the decision-maker (in situation OR action) = P2 fail; "they/their/them" denoting you+someone = P2 fail; a lone coordinated 3sg verb slip ("and makes", "you goes", "and isn't") = pass with "minor" note (9 rows: 17 29 30 38 65 69 74 88 94); >=2 slips, dropped subject, or non-imperative narrated outcome = actions fail. Had I failed the minor slips too, P2 would be ~70 and actions ~89.

Failure patterns (most common first)
1. Actor's his/her/him/himself/hers/she left in 3rd person, mostly in action text, when another same-gender person is in the clause (18 rows): ms_308Q0PEVB9B26E6ODJPN665SFSII95 ("Ask Ted if he can check out his new iPhone"), ms_3PZDLQMM0UJ0TRZP00EMLGZJVXSC24 ("wants to borrow her credit card ... she is not comfortable lending out her"), ms_39U1BHVTDMP60QXJQMNHT04FPK4T31 ("sneeze mucus into his own hand"); also 7 12 18 26 37 39 43 45 64 82 92 99.
2. Plural "they/their/them" standing for actor+other after conjoined subject (5 rows): ms_3IO1LGZLKAVMZPSD6QAK97KCLSK68I ("they are spending a lot of time together"), ms_3D3VGR7TA1DTKBKRMXIMTL3X0L1R3N ("they are in a long distance relationship"), ms_3PDJHANYK6EFS0T69U4QMKDBMUZH6X ("they'll discuss it further at home"); also 21 77.
3. Name substitution garbling possessive/appositive/relative slots (5 rows): ms_3NXNZ5RS1BV5HUPSUSLQFHFJ14979L ("Your found out your Dad"), ms_34J10VATJGW8YDNAUL09S1VHPKRIQG ("but his wife you do"), ms_39K0FND3AID27G6KQ41FUUNT0XNAML ("You who lives with family ... and wants"); also 7 ("his wife you want you to"), 26 ("Your invited their friend").
4. Over-replacement: object pronoun for the OTHER person replaced by "you" (3 rows): ms_3QRYMNZ7FZFD4UQT857W2E2LU2ETN2 ("you tell you that you want"), ms_3ZWFC4W1UV5O0N0K6SJOUUSU52SRF2 ("you will beat on you"), ms_3VHP9MDGROIKULB1OVTT5ZT83YDFC0 ("you don't believe you").
5. 3sg verb residuals in coordinated verbs after imperativization (11 rows, 3 failed): ms_35L9RVQFCPG0UBJ75C2T2QRRSFTUHP ("which divvies up and sells"), ms_32Q90QCQ1TJA75NTLXQLB0LGXZAEKK ("before you heads out ... and only sneezes"), ms_3VHP9MDGROIKULB1OVTT5ZT83YDFC0 ("so you calls ... but still chooses"); minor passes in 17 30 38 65 74 82.
6. Outcome narrated inside the action, action not a clean imperative (5 rows, 3 failed): ms_3COPXFW7XCAE4WCJUB6W5CKKANXPKY ("Finish your interview and are offered the job ... which you accept"), ms_34S9DKFK74N9LGPNIBUVAVU09VGNYN ("and her daughter says she is"), ms_3HWRJOOET608VO01Q6ZN2MCQFFLES8 ("and your knee injury goes from a minor one to a major one", passed with note); also 68 98.
7. Actions not alternatives for the stated decision (source quality, 1 fail + 1 note): ms_3Z4GS9HPNW813B1ZFVN61LOD4EA77W, ms_3WYP994K18P1EVJVJU8E8K8EF466YA.
8. Formatting: situation carries CSV double-escaped quotes and lowercase sentence-initial "you" (1 row): ms_3SB4CE2TJWTD1S5O4B3O5B3R7LEAXG.

Systematic conversion bugs and rule fixes
- (Patterns 1, 4) Pronoun mapping is lexical, not coreferential. Fix: in Moral Stories the actor is the named subject of the first sentence of `situation`; run a cheap coref (spaCy + neuralcoref/fastcoref, or a heuristic: pronoun refers to the actor iff the actor is the nearest preceding singular same-gender mention OR the pronoun is subject of an embedded clause under a speech/request verb whose matrix subject is you, e.g. "Ask Ted if he can"). Map only actor-referring pronouns -> you/your/yourself, and never touch pronouns whose antecedent is the other person. Given 13/16 flagged rows fail, the cheapest fix is to treat `pronoun_same_gender_other` as a HARD_FLAG (exclude), as the plan already does for `pronoun_ambiguous`; that alone lifts P2 to ~86%.
- (Pattern 2) When the actor is part of a conjoined subject ("X and you", "you and your partner") or a couple, map subsequent they/their/them -> you/your/you and fix the copula ("they are" -> "you are"). Flag any remaining sentence-initial "they" with no plural noun antecedent.
- (Pattern 3) Name replacement must handle: (a) "Name's" before a noun -> "your", "Name's" as contraction -> "you are/have" (never "Your <verb>"); (b) appositive "his wife Name" / "Name, who VBZ" -> drop the appositive or rewrite to "you" and lemmatize the following VBZ ("You who lives" -> "You, who live"); (c) Name inside another name's possessive NP ("Name's wife Name2") -> only substitute the actor.
- (Pattern 5) Agreement fix currently only hits the head verb. Fix: after imperativizing the head, lemmatize every VBZ token whose nsubj is "you" or absent and that is coordinated (conj via and/but/so/which) to the head; same pass over the situation for "you VBZ".
- (Pattern 6) Moral Stories moral/immoral_action frequently appends a consequence clause with a new subject ("and your knee ... goes", "and the two end up", "which you accept", "who take the dog"). Fix: truncate the action at the first coordinated/relative clause whose subject is not you/elided, or add an informational flag `outcome_in_action`; also rows like 54 reveal the decision lives in that clause (accept vs decline), so truncation should fall back to flag if the two actions become identical.
- (Pattern 8) Unescape `""` -> `"` and strip wrapping quotes from source fields before any rule; capitalize "you" when it is the first alphabetic token of a sentence.
```

---

## 报告 3

```
JUDGE REPORT — source scruples (100 rows), sheet saved in place: /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_scruples.csv (same columns, same row order, QUOTE_ALL)

PASS RATES
- pass_second_person: 25/100 (25%). Lenient variant that ignores residual we/our/us and fails only I/my/me/am residue: 91/100.
- pass_two_exclusive_actions: 89/100 (89%)
- pass_no_verdict_in_situation: 95/100 (95%)
- all three jointly: 19/100 (19%). Joint under the lenient second-person variant: ~77/100 (gate of 90% still not met).

MOST COMMON FAILURE PATTERNS
1. Residual first-person plural (we / our / us) referring to the decision-maker's group — 66 rows; by far the dominant failure. Examples: scr_ba4ix5 ("in our friend group"), scr_a3n3c0 ("risk our friendship ... we had only talked"), scr_b942jv (10+ we/us in one post).
2. Residual first-person singular that the rule missed — 9 rows: "Ive", "id", "am", uppercase "MY", and "I'm" mangled into "you'm". Examples: scr_b5ci9p ("Ive had this computer"), scr_a7unln ("you'm visiting canada"), scr_anfsou ("text MY PHONE"). Related breakage without a fail: "i.e." -> "you.e." (scr_ay409k), "me" -> "you" inside idioms ("don't get you wrong", "bear with you": scr_b0sclt, scr_b52db3, scr_b02phm).
3. Pronoun conversion applied inside quoted speech, making "you" ambiguous (another speaker's "I" becomes "you") — 7 rows: scr_9yvck2 ("Damn, you wish things would have worked out"), scr_ag2dsr ("Your housemate told 'No. You do not like her'"), scr_b9xesz ("rip, you should've told you").
4. Broken coordinated gerund in actions (only the first word was de-gerunded) — 7 rows: scr_ag4kr0 ("Show up for free food and leaving."), scr_b4iwv2 ("Exclude one sister and taking the other"), scr_a9fvma ("Keep a log ... and asking them to sign"); also scr_avutna, scr_ayulwq, scr_atbj1r, and a parenthetical "(and exaggerating to)" in scr_aa85wk (passed, intelligible).
5. Action not a decision the "you" faces / third-party or bystander post — 2 rows failing both actions and no-verdict: scr_ah1ml4 ("You wasn't actually involved in this apart from being a bystander ... Was it a dick move on their part?"), scr_atbj1r (girls abandoned their bags; "Luckily, this worked out"). Related: scr_b0zufj (argument already happened; situation opens mid-stream after sentence stripping).
6. AITA jargon left in situation — 2 rows: scr_b6s4is ("would make you TA"), scr_aq2aya ("WAITA if you keep it?").
7. Non-imperative / unintelligible action pair — 3 rows: scr_axfnm2 ("You stopped doing errands personally not signing up for." / "Do not you stopped ..."), scr_b2njyu ("Ask your bf you didn't split expenses 50/50."), scr_b2xgd7 ("terribly toning deaf, roommating").
8. Negative-polarity item left after stripping "not" to build the affirmative — 1 row: scr_9y269x ("Talk to your grandma anymore.").
Informational (not failed): Reddit meta sentences surviving the filter in ~9 rows (scr_aso4vg "Your friend told you you should post your dilemma here, so you have", scr_b9t78a "Thanks in advance ... Thanks.", scr_ayf02x "TL/DR:" variant, scr_aa85wk "This post is not about drugs"); unintroduced he/she/they/it because the referent lived only in the stripped title (~8 rows, e.g. scr_atf8s8, scr_awtmmn, scr_asubq9) — acceptable since the action names the person, but worth prepending nothing / noting.

SYSTEMATIC CONVERSION BUGS AND RULES THAT WOULD FIX THEM
- we/our/us/ourselves are not converted in the situation (documented as "informational flag", but it is the reason the second-person gate fails). Fix: either (a) add a regex pass mapping we -> "you and they"-style is unsafe; the practical rule is to DROP from the pool any situation with residual we/our/us (as HARD_FLAG), or (b) keep them and relax the second-person criterion to singular residue only — then this source passes 91%.
- Singular rule misses tokens: contraction-without-apostrophe forms ("Ive", "Im", "id", "ill"), stand-alone "am" (from "I am" where "I" was dropped), uppercase "MY"/"I'M", and "I'm" -> "you'm" (I'm must map to "you're", and "I was/wasn't" to "you were/weren't"; "was"->"were" agreement also broken in 4 rows: "you still wasn't", "You wasn't"). Fix: case-insensitive matching, a contraction table (I'm->you're, I've->you've, I'd->you'd, I'll->you'll, Ive/Im/id), and an exclusion list for "i.e."/"me" inside fixed idioms ("don't get me wrong", "bear with me").
- Pronoun conversion runs inside quotation marks. Fix: skip spans between matching quotes (", ', ") when converting I/my/me -> you/your, or flag and drop posts with quoted first-person speech.
- degerund_first_word only fixes the first verb; coordinated gerunds after "and"/"or"/"then" and parenthetical gerunds stay as -ing. Fix: de-gerund every -ing verb that immediately follows a coordinator (and/or/then/but) in the action, or drop actions containing " and \w+ing".
- normalize_action does not handle actions that begin with a pronoun + gerund ("Me stopping doing errands I personally didn't sign up for" -> "You stopped doing errands personally not signing up for"). Fix: strip a leading object pronoun (me/us/my/our) before de-gerunding, and reject if the result does not begin with a verb lemma.
- Building the affirmative from a negative title by deleting "not" leaves NPIs (anymore, ever, any). Fix: when stripping "not", map anymore -> "" or "again", "ever" -> "", "any" -> "some", or drop the family.
- The meta-sentence filter misses "TL/DR", "Thanks (in advance)", "First time poster", "This post ...", "if anyone wants to give ... advice", "Your friend told you you should post your dilemma here" (originally "my friend told me I should post ..."). Fix: extend the regex to TL[/;: ]?DR, ^Thanks, poster, "this post", "post your", "legal advice".
- Jargon filter misses bare "TA" and "WAITA"/"WIBTA" inside the body (only sentence-level NTA/YTA/ESH/NAH are removed). Fix: add \b(W?AITA|WIBTA|TA|the asshole)\b to the sentence-drop list.
- Sentence stripping (title/question removal) can remove the only sentence that introduces the referent or the decision itself, leaving posts that open mid-stream ("Since you did everything...", "She craves drama...", "They show no love towards her..."). Fix: reject when the first sentence starts with a pronoun whose antecedent does not appear in the situation, or when the removed inner question was the only sentence naming the decision.
- Bystander/third-party posts (narrator judging someone else's act) pass the WIBTA filter because of the title regex. Fix: drop when the body contains "wasn't involved", "bystander", "not about me", or when the action's agent (from the title) is not "I/me".
```

---

## 报告 4

```
JUDGE REPORT — source aita_berkeley (100 rows, judged by hand, no API)
Sheet saved in place: /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_aita_berkeley.csv (same columns, same row order, csv QUOTE_ALL; every 0 has a note).

PASS RATES
- pass_second_person: 42/100
- pass_two_exclusive_actions: 89/100
- pass_no_verdict_in_situation: 62/100
- all three jointly: 20/100
By wave: wave 1 (WIBTA, n=17): sp 5, act 16, nv 16, all 4. wave 1_pilot (n=24): sp 14, act 23, nv 13, all 8. wave 1_gated (n=59): sp 23, act 50, nv 33, all 8.
None of the three columns reaches the 90% gate in e2c_plan §1 step B; the source fails the gate.

JUDGING POLICY (so the numbers can be re-read)
- second_person = 0 when (a) any residual singular I/me/my, (b) two or more unquoted we/our/us referring to the decision-maker, or (c) I/me inside quoted dialogue was blindly rewritten to "you", making it ambiguous who is speaking. A single incidental "we/our" with an obvious referent passed with the note "minor". If we/our residue were tolerated entirely, second_person would be 89/100 (the 47 we/our-only fails flip), so this column is dominated by one fixable pattern.
- no_verdict = 0 when (a) AITA jargon (TA/AH/NTA...) appears, or (b) the situation narrates a completed one-shot deed AND its aftermath (others' reactions/consequences), so "What should you do? Do X / Do not X" is temporally incoherent. Posts where the deed is done but the decision is still standing/reversible (keep disinheriting, keep the ban, keep the clothes) passed with the note "retrospective" (33 such passes).

MOST COMMON FAILURE PATTERNS
1. Residual first-person plural (we / our / us) in the situation — 47 rows fail second_person on this alone, e.g. bk_11sjjtx, bk_10b1m5q, bk_10dkvdd (plus 2 more that also had singular residue: bk_zbxujf "Ive tried", bk_10j09v2 where the boyfriend "Max" is never introduced as yours).
2. Retrospective post with outcome/aftermath already narrated (one-shot deed done, reactions told) — 34 rows fail no_verdict, e.g. bk_11krdws, bk_109prwu, bk_zkgml8 ("What you did: ... As a result ..."). Concentrated in 1_gated (26/59) and 1_pilot; wave-1 WIBTA posts almost never fail here (1/17). This confirms the §10 risk is real and large, not marginal.
3. First-person pronouns inside quoted speech rewritten to "you" — 9 rows fail second_person with ambiguous dialogue, e.g. bk_znimxx ("Don't lie to you", "why didn't you wake you up?"), bk_120yus6 ("your doctor told you that"), bk_11hwc4q ("you hope playing a game was worth our friendship. You can't believe you're so selfish"). Also bk_101x7yh, bk_zfu1ki, bk_10o3ez6, bk_10inzba, bk_10xdapp, bk_105rdb5.
4. Residual meta/preamble sentences not caught by the meta-sentence filter — e.g. bk_119mpnz ("Throw-away because you don't want anyone you know finding you"), bk_zec0hx ("Please don't post this anywhere!"), bk_zyts1q ("You hope you can convey everything in this post"), bk_zps7cj ("You will make this very short"), bk_zj90x3 ("(Advice also welcome!)"), bk_10c7j1i ("You'll start with the fact"). Noted, not failed unless another rule hit.
5. AITA jargon left in situation — 4 rows fail no_verdict: bk_119mpnz, bk_10m5avu ("TA" x2), bk_1042ba7 ("AH"), bk_zbxujf ("AH move").
6. Broken action pairs — 11 rows fail two_exclusive_actions, four sub-patterns: (a) gerund/degerund not applied or verb mangled: bk_10c7j1i ('Siding" with ...' / 'Do not siding"'), bk_zfu1ki ('Make a scene" and embarassing your mom'), bk_yt8taf ("Watch to organize a family reunion"); (b) title adverbial that only makes sense with the negation kept in the affirmative: bk_11g6wo5 ("Buy ... the good donuts any more"), bk_yo3gf2 ("Sell your ex the cottage ... but being willing to sell it to somebody your ex hates"), bk_10inzba (Title Case + dangling "not Wanting to Support Hers"); (c) action is an outcome label, not a choosable act: bk_109prwu ("Piss of the bride"), bk_11svxoq ("Ruin a proposal"); (d) action references something absent from the (over-stripped or truncated) situation: bk_11s8b0w (2-sentence situation, no woman), bk_znimxx (phone never mentioned), bk_105rdb5 ("Book/Do not book" when he simply forgot and booking is now impossible). Related situation-coherence issue: bk_10mpofv, the burned gift is never described (a sentence was stripped).

SYSTEMATIC CONVERSION BUGS AND RULES THAT WOULD FIX THEM
1. Person conversion skips plural: the I/my/me -> you/your rule leaves we/our/us/ourselves untouched (the `first_person_plural` flag is informational). Fix: in situation text, map unquoted we -> "you and [X]"/"you both" is unsafe, but "we"/"our"/"us" -> "you"/"your"/"you" is acceptable in >90% of these posts (the plural is almost always author+partner/family and the second person already stands for the author); at minimum apply "our" -> "your" and "we" -> "you" with verb agreement ("we were" -> "you were", "we've" -> "you've"), and drop the `first_person_plural` rows from the pool rather than flagging them if that mapping is not applied.
2. Pronoun rewriting inside quotation marks: the rule rewrites I/me/my inside quoted dialogue, where the speaker is often someone else. Fix: skip spans inside "..." / '...' / smart quotes (and after "said/texted/messaged ... :" ) when mapping pronouns; or drop posts whose quoted spans contain first-person pronouns (the existing `source_has_second_person` flag approximates this: 9/9 broken-quote rows carry it, but it also fires on harmless rows).
3. Residual first-person artifacts from fixed phrases: "Let me be clear" -> "Let you be clear", "let me explain" -> "let you explain", "I am" -> "You am" (bk_z9v6gi), "what I mean" -> "what you mean", "Me again, I am due" -> "You again you are due", and the "I" -> "you" with verb left as "am"/"was" ("am thinking", "you was free", "you wasn't"). Fix: handle "let me" -> "let yourself"/drop sentence; "I am/I'm" -> "you are/you're"; "I was" -> "you were".
4. Meta-sentence filter too narrow: it removes edit/TLDR/AITA sentences but not throwaway/privacy/"this post"/"advice welcome"/"I'll start with"/"I'll make this short"/"I need strangers' opinion" preambles, and it does remove content sentences in some posts (bk_10mpofv lost the gift description; bk_11s8b0w left a 2-sentence stub). Fix: add a regex list for post-meta (throwaway|throw-away|don't post|this post|advice (also )?welcome|make this short|start (off )?(with|by saying)|unbiased opinion|TBH) and drop families whose cleaned situation is < ~40 words or whose action nouns (umbrella/woman, phone, gift) do not appear in the situation.
5. Verdict-jargon filter misses "TA" and "AH" standalone tokens: it catches NTA/YTA/ESH/NAH but not "you may be TA", "think you're AH", "an AH move". Fix: add \bTA\b, \bAH\b, \bA-?hole\b, "the asshole" to the removal/drop list.
6. Title->action derivation of compound titles: titles with "any more", "but ...", "because ...", "even though ..." or an outcome verb (ruin, piss off, make a scene, embarrass) yield a nonsensical or non-exclusive affirmative. Fix: strip trailing "any more/anymore" when building the affirmative; drop titles containing " but " or whose head verb is in an outcome-verb list (ruin, piss off, upset, embarrass, offend, make a scene, hurt); keep "because/even though" clauses only on the polarity they came with, or truncate the action at the first subordinator. The gerund rule also needs a fallback: "Siding\"" and "Watch to" show the first-word degerund failing when the title has a stray quote or an unrecognized verb; require the result to be in a verb lexicon and drop otherwise.
7. Retrospective-vs-prospective mismatch (the §10 risk): 34/83 retrospective rows already narrate the aftermath, so the prompt asks what to do about a deed whose consequences are known. No rule can fix this without rewriting; the realistic choices are to keep only wave-1 WIBTA (16/17 passed no_verdict) plus retrospective posts whose action is standing/reversible (my "retrospective" notes, 33 rows), or route the one-shot retrospective posts to the Layer-3 LLM rewrite. A cheap heuristic to separate the two: fail if the situation contains past-tense aftermath cues after the deed ("ended up", "stormed off", "won't talk", "blocked", "furious", "now ... is mad/angry/upset", "As a result") and the action verb is a one-shot speech/consumption act (say/tell/call/eat/laugh/wear/post/leave).

Scratch script used to fill the sheet: /private/tmp/claude-501/-Users-yuansir-workspace-CS329X-Project/64062123-fa10-4af6-86b2-26906e1a925d/scratchpad/fill_bk.py
```

---

## 报告 5

```
VERIFIER REPORT — E2C handcheck sheets (4 sources x 100 rows)
Sample: numpy default_rng(20261002).choice(100, 25, replace=False) -> same 25 row indices for every sheet (n=100 each): [1,4,8,10,15,17,23,24,27,37,49,53,55,58,60,64,68,75,78,81,84,86,88,92,99]. I judged situation/actions first, then compared. Sheets were NOT modified. Full-sheet rates recomputed with pandas from the saved CSVs.

TABLE (full sheet, n=100 each; agreement = my blind verdict vs judge on the 25 sampled rows, per column sp/act/nv and on the joint all-three verdict)

source           | n   | pass_second_person | pass_two_exclusive_actions | pass_no_verdict | joint pass | agreement on 25 (sp/act/nv/joint) | gate (>=90%): sp / act / nv / joint
scruples         | 100 | 25                 | 89                         | 95              | 19         | 25/25/25/25                       | FAIL / PASS(89 is <90, marginal fail) / PASS / FAIL
aita_berkeley    | 100 | 42                 | 89                         | 62              | 20         | 21/25/24/24                       | FAIL / marginal fail (89) / FAIL / FAIL
moral_stories    | 100 | 75                 | 94                         | 100             | 71         | 23/24/25/23                       | FAIL / PASS / PASS / FAIL
hendrycks_ethics | 100 | 94                 | 97                         | 98              | 89         | 25/25/25/25                       | PASS / PASS / PASS / 89 (just under; per-column gate met)

Strictly per the task definition ("no residual we/our"), the judge-reported sp numbers are a ceiling for aita_berkeley and a floor-consistent value elsewhere: recomputing sp with zero tolerance for we/our/us gives scruples 22 (joint 16), aita_berkeley 22 (joint 10; the judge passed 20 rows with a single "minor" we/our), moral_stories 75 (unchanged), hendrycks_ethics 94 (unchanged). Under the opposite, lenient policy (ignore we/our, fail only singular residue) the judges report sp ~91 (scruples) and ~89 (aita_berkeley); joint under that policy is ~77 and ~41 respectively, still below the gate.

DISAGREEMENTS (all 8 are policy-level calibration, none is a factual misreading; I would not overwrite)
aita_berkeley (sp 21/25, nv 24/25):
- bk_11g6wo5, bk_zn0s4u, bk_yo3gf2, bk_zps7cj: judge sp=1 with note "minor" for a single we/our ("we've had him tested", "our baby", "We were very close", "while we are in prep"). Under the task's literal rule these are sp=0 (my verdict). Not an error, but inconsistent with the scruples judge, who failed every we/our, so the scruples 25 vs aita 42 are not directly comparable (strict-equal: 22 vs 22).
- bk_11t5594: judge nv=0 (aftermath narrated); I passed it as "retrospective" because the decision (defend sister / keep siding with husband) is still live. Borderline; judge's call is defensible.
moral_stories (sp 23/25, act 24/25):
- ms_3PW9OPU9PRIG6OPRK3P24KGSR0912B: action_x "doesn't impact their love for him" — "their" = you + husband. Judge sp=1 with empty note, which contradicts the judge's own stated policy ("they/their/them denoting you+someone = P2 fail", applied to ms_3IO1..., ms_3PDJ...). Closest thing to a verifiable judging error; would lower sp to 74 / joint to 70.
- ms_3N4BPTXIO9QRW1KFBX5QFI7JKABKUP: action_y "Flirt back at Tina, and the two end up having sex" — I count "the two" as third-person reference to you+Tina plus narrated outcome (sp=0); judge passed with a note. Policy call.
- ms_3KAKFY4PGV0GRCH8WAODFT26DA43IN: action_x "and they talk about her grandmother's childhood" has two slips (they, her); judge's own ">=2 slips = actions fail" rule would make act=0 (my verdict); judge gave act=0? No: judge gave sp=0, act=1. Minor inconsistency.
scruples and hendrycks_ethics: 25/25 on every column; the judges' notes matched what I saw (e.g. scr_ag4kr0 "and leaving", scr_b2njyu unintelligible action, scr_b6s4is/scr_aq2aya TA/WAITA jargon, eth_j_bd7bb9fb5344 "To knock"/"Do not to knock", eth_j_f156385a6932 "our anniversary"). The 3 scruples rows passed despite a we/our token are correct (quoted neighbor speech, "US" the country, generic idiom "we all have our own cross to bear").

OBSERVATIONS CONFIRMED IN MY BLIND READ
- Residual we/our/us dominates both Reddit sources: 76/100 scruples and 75/100 aita_berkeley situations contain it; 67 and 52 rows respectively fail second-person on that alone. hendrycks_ethics has 6 such rows (all its sp failures); moral_stories has none.
- aita_berkeley no_verdict: 34 one-shot-deed-plus-aftermath failures concentrated in waves 1_gated (26/59) and 1_pilot; wave-1 WIBTA posts fail nv 1/17. Joint pass by wave: 1: 4/17, 1_pilot: 8/24, 1_gated: 8/59. 33 further rows passed only as "retrospective". Confirmed on my sample (bk_zfityy, bk_11svxoq, bk_10mpofv, bk_10wgf2a, bk_11eoqw8, bk_10s2507, bk_zps7cj, bk_105rdb5 all read as deeds already done with consequences known).
- Quoted first-person speech converted to "you" (scr_9yvck2, scr_ag2dsr, bk_10inzba, bk_105rdb5) makes the speaker unrecoverable; seen in 4/50 sampled Reddit rows.
- moral_stories sp failures are coreference failures of a lexical pronoun map (same-gender other person, conjoined subject -> they/their); 13/16 pronoun_same_gender_other-flagged rows fail; even treating that flag as HARD_FLAG leaves sp ~86%.

SYSTEMATIC CONVERSION ISSUES WORTH FIXING BEFORE SCREENING (ranked by rows recovered)
1. Plural first person (we/our/us/ourselves, we're/we've/we'd) is left untouched in situations and copied into ETHICS actions. Either map case-preserving we->you, our->your, us->you with "we were/we've" agreement outside quotes, or HARD_FLAG first_person_plural and drop. This alone decides whether scruples/aita can ever reach the gate (strict sp 22% vs lenient ~90%). Decide the policy once and apply to all four judges' sheets consistently (currently scruples strict, aita lenient).
2. Retrospective one-shot posts (aita_berkeley 1_pilot/1_gated, also some scruples): situation narrates the deed and its aftermath, so "What should you do?" is incoherent. No rule fixes this; restrict Reddit to WIBTA titles (wave 1) plus posts where the action is a standing/reversible decision, or route the rest to the LLM-rewrite layer. Cheap filter: aftermath cues (blocked, furious, won't talk, stormed off, "now ... is mad", "As a result") + one-shot action verb (say/tell/eat/wear/burn/leave/laugh).
3. Pronoun rewrite inside quotation marks: skip spans between matching quotes (straight and smart, and after said/texted ... :), or drop posts whose quoted spans contain I/me/my.
4. Singular contraction/agreement gaps: Ive/Im/id/ill without apostrophe, uppercase MY/I'M, "I'm"->"you'm", "I was/wasn't"->"you was/wasn't", bare "am", "let me"/"don't get me wrong"/"bear with me"/"what I mean" idioms, "i.e."->"you.e.". Case-insensitive contraction table plus idiom exclusion list.
5. De-gerund only hits the first word: coordinated gerunds after and/or/then/but ("Show up for free food and leaving", "Keep a log ... and asking", "Host bbq and being anti-social", "but being willing to sell"). De-gerund every -ing verb right after a coordinator, or drop actions matching " (and|or|but|then) \w+ing\b".
6. Affirmative built from a negated title keeps NPIs/negation-only adverbials ("any more", "anymore", "ever", "any"), and compound titles with " but "/outcome verbs (ruin, piss off, embarrass, make a scene) yield non-choosable or self-contradictory actions. Strip NPIs when deleting "not"; drop titles containing " but " or an outcome-verb head; validate that the action begins with a base-form verb from a lexicon (catches "To knock", "Siding\"", "You stopped", "Watch to").
7. Jargon and meta filters: add \b(W?AITA|WIBTA|TA|AH|A-?hole|the asshole)\b to the sentence-drop list; extend meta regex with TL[/;: ]?DR, ^Thanks, first time poster, throwaway, don't post, this post, advice (also )?welcome, make this (very )?short, as you're writing this, start (off )?(with|by). Also reject situations whose first sentence opens with a pronoun with no antecedent (title stripping removed the referent: scr_ayulwq, scr_aunr1s, bk_10j09v2 "Max") or whose action noun (gift, phone, woman) never appears in the situation.
8. moral_stories coreference: substitute only actor-referring pronouns (nearest same-gender singular antecedent, or embedded subject under ask/tell with matrix subject you); map they/their after conjoined "X and you"/couple subjects to you/your; lemmatize coordinated VBZ after imperativization; truncate actions at a coordinated clause with a new subject ("and the two end up", "and they talk"); treat pronoun_same_gender_other as HARD_FLAG in the meantime.
9. hendrycks_ethics (already near gate): strip leading "to " in the habit VP, extend stative filter to become/get/feel + adj, cut VP at ", because/since/as", collapse "..", and apply the we/our->you/your map to both VP and reason. These six plus three fixes would lift joint from 89 to ~97.

Sampled-row file (for re-audit): /Users/yuansir/.claude/projects/-Users-yuansir-workspace-CS329X-Project/64062123-fa10-4af6-86b2-26906e1a925d/tool-results/bddig56nv.txt; comparison script: /private/tmp/claude-501/-Users-yuansir-workspace-CS329X-Project/64062123-fa10-4af6-86b2-26906e1a925d/scratchpad/verify.py. Sheets unchanged: /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_{scruples,aita_berkeley,moral_stories,hendrycks_ethics}.csv.
```
