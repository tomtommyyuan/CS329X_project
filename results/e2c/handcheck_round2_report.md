# E2c 转换人工抽检 第二轮（2026-10-05，4 位判官 agent + 1 位盲审复核）

判定表在 `data/annotation/e2c_handcheck_{scruples,aita_berkeley,moral_stories,hendrycks_ethics}.csv`（seed 20261006，与第一轮已判行零重叠；第一轮存档于 `data/annotation/e2c_handcheck_round1/`）。门：每源三列各 ≥ 90%。

**结果：scruples / aita_berkeley / hendrycks_ethics 三源过门；moral_stories 二人称列 79% 未过。** 复核抽 25 行盲判，四表三列与联合判定均 25/25 一致。

| source | n | 二人称 | 两行动互斥 | 情境无裁决 | 联合 | 第一轮联合 | 复核一致 (sp/act/nv/joint) | 门 |
|---|---|---|---|---|---|---|---|---|
| scruples | 100 | 95 | 96 | 98 | 90 | 19 | 25/25/25/25 | **过** |
| aita_berkeley | 46 | 100 | 100 | 100 | 100 | 20 | 25/25/25/25 | **过**（n=46，单侧 95% 下界 ≈ 93.7%） |
| moral_stories | 100 | **79** | 96 | 100 | 76 | 71 | 25/25/25/25 | **二人称未过** |
| hendrycks_ethics | 100 | 100 | 100 | 100 | 100 | 89 | 25/25/25/25 | **过** |

moral_stories 细分：带 `pronoun_same_gender_other` 的 18 行二人称仅 4 过；其余 82 行二人称 75/82 = 91.5%、联合 72/82 = 87.8%。该 flag 改硬性后仍有 7 行二人称失败（3 行他人代词被改成 you、4 行 they/their 指 you+他人 未被 `plural_refers_to_actor` 捕获），样本上限 91.5% 贴着门，须一并修规则。池内该 flag 分布：wave 1 134/600、2a 525/2,424、reserve 1,016/4,746；改硬性后 wave 1 需从 2a 未标记的 1,899 条补足。

**建议**：(1) moral_stories 不入本轮筛选：`pronoun_same_gender_other` 改硬性 + 判官报告修复 (2)–(8)（他人代词过度替换、无 "you and X" 触发的 they/their、"yours in-laws"、"'s"→"you've"、"Be having"、并列 VBZ、去噪后 x==y），重建后只对 moral_stories 以新 seed 重抽 100 行（第三轮）；(2) 步 D 可以对已过门的三源先开跑：用 `contested_pool_T1.jsonl` 过滤掉 `source == moral_stories` 的 prompt（moralchoice 675 + scruples 585 + aita_berkeley 50 + hendrycks_ethics 300 = 1,610 族 × 2 = 3,220 条，× 3 teacher = 9,660 次 ≈ $13），moral_stories 过门后追加其 wave 1（600 族 / 1,200 条）到同一输出文件；前提是 §9 的提交要求已满足。(3) scruples 剩余 5 处二人称失败中 3 处是无引号的转述话语（"like yeah you'll be able to pay you back"），2 处是 lemme / imo；都可用规则修，但 95% 已过门，不必为此重建。

---

## 报告 1

```
JUDGE REPORT — source scruples, ROUND 2 (seed 20261006; 100 rows, judged by hand, no API)
Sheet saved in place: /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_scruples.csv (same 11 columns, same row order, csv QUOTE_ALL; situation/action/needs_review text byte-identical to the unjudged sheet; every 0 carries a note; unjudged backup at /private/tmp/claude-501/-Users-yuansir-workspace-CS329X-Project/64062123-fa10-4af6-86b2-26906e1a925d/scratchpad/scr_round2_unjudged_backup.csv).

PASS RATES (strict policy, same rubric as round 1)
- pass_second_person: 95/100 (round 1: 25)
- pass_two_exclusive_actions: 96/100 (round 1: 89)
- pass_no_verdict_in_situation: 98/100 (round 1: 95)
- all three jointly: 90/100 (round 1: 19)
Each column clears the >= 90% per-column gate; joint is exactly 90.
Residual first-person plural (we/our/us/ours/ourselves): 0/100 rows (76/100 in round 1) — the new HARD flag works. Residual singular I/my/me/am: 0 rows of real pronoun residue; a regex sweep over all 300 texts finds only false positives ("an ID", "1-2 am", "i.e.", German "im") plus the two idiom/acronym tokens below.
Policy sensitivity: 2 of the 5 second_person fails are fixed-expression residue ("Lemme", "imo"); if those are tolerated, second_person = 97 and joint = 92.

FAILURE PATTERNS (most common first)
1. Another speaker's first person converted to "you" in unquoted reported speech (3 rows, all second_person=0): scr_a6t0nc ("like yeah you'll be able to pay you back half" = sister's "I'll be able to pay you back"), scr_b2eati (professor's email "But you havernoted your issue" = "I have noted"), scr_b2rpee ("a text of friend one saying you think you know who said" = "I think I know"). The quoted-speech skip only protects spans inside quote marks; speech introduced by "saying / like yeah / responds back:" without quotes is still converted.
2. Fixed-expression first-person residue (2 rows, second_person=0, strict): scr_a5o2t7 ("Lemme also note" = let me), scr_akt8eq ("(again, imo)" = in my opinion). Idiom list lacks lemme / imo / imho / afaik.
3. Broken or non-choosable action pair (3 rows, actions=0): scr_a3rv3h ("Go and got vaccinating against the wishes ..." — coordinated verb mis-inflected, not an imperative), scr_at602v ("Use a wheelchair, but not date someone in a wheelchair" / "Do not use a wheelchair, but ..." — title with " but " negated on the wrong clause), scr_b9lft7 ("Say no more substituting for someone who requested" — not an imperative).
4. Action references something absent from the over-stripped situation (1 row, actions=0): scr_b47j4w — actions are about "ditching your friend" but the situation (ending in "So...") only discusses swapping class periods; the closing question that introduced the friend was stripped.
5. Bystander post / decision already taken (1 row, actions=0 and no_verdict=0): scr_b9lft7 ("Asking for your mom...", "She rejected the job request") — the bystander filter catches "asking for a friend" but not "asking for my mom/sister/...".
6. AITA jargon + meta post (1 row, no_verdict=0): scr_a9wrpl ("it's great to get unanimous NTAs or YTAs"; the post is about the subreddit itself, "Advocate for the least popular consensus in these posts"). Jargon filter misses plural NTAs/YTAs.

INFORMATIONAL (passed, noted in the sheet; not column failures)
- Surviving meta sentences in ~10 rows: scr_au6ohl ("Your original post was removed ..."), scr_b4tcti ("Okay this is post will require some backstory"), scr_ay7hd8 ("You'd appreciate any insights. Cheers all."), scr_b7hezi ("First you wanna say"), scr_b2r2ft ("You'll spare the details"), scr_ar10t9 ("You know the title is weird so you'll explain"), scr_ah0ytf ("please read all of it before passing judgement"), scr_abj5lw ("All opinions are welcome"), scr_az19fq ("P.s. You just woke up so sorry ...").
- Opens mid-stream / referent lives only in the action in ~6 rows, still intelligible: scr_azfs64 ("her"), scr_b9joc7 ("Pretty much this -"), scr_adxxds ("this choir"), scr_ayp37v ("he"), scr_alnb0z ("This was a couple years ago ... he was living"), scr_au6ohl ("She").
- Agreement slips where "I" was dropped from a coordinated clause (5 rows): "You knew ... and wasn't sure" (scr_ahgfr9), "flew ... and was there" (scr_ak64y2), "and was thinking" (scr_auchy8, scr_9vodbi), "Was tested" (scr_b95wb5). No pronoun residue, so passed.
- Lost object pronoun: scr_aarc0s "not deal with him treating this way" ("me" deleted instead of converted); scr_b9tos3 "you do various you campus events" (garbled). Minor.
- Over-stripped one-sentence situations: scr_b8r2yj ("Ask your grieving friend for help" — help with what?), scr_aw69yx (height vs weight mismatch from source title). Passed as intelligible.
- Retrospective but passable: scr_b6tgeq (flight "the other day", deed not narrated as done), scr_b2eati (already replied politely; decision still open).

REMAINING CONVERSION BUGS AND RULE FIXES
- Unquoted reported speech: extend the quoted-span skip to clauses introduced by "saying / said / texted / responds back: / like yeah / like," up to the sentence end, or HARD-drop situations where a first-person pronoun sits inside such a clause before conversion (pattern 1, 3 rows = 60% of second_person fails).
- Idiom exclusion list: add lemme, imo, imho, afaik, iirc (treat as meta tokens to strip or drop the sentence); currently "Lemme" and "imo" survive.
- Coordinated verb inflection in the action: "Go and got vaccinating" — the de-gerund pass handles "-ing" after and/or/then/but but not a past-tense/other misinflected second verb; validate every coordinated verb is base form, or drop.
- Titles containing " but " (scr_at602v) still produce a self-contradictory affirmative/negative pair; drop titles with " but " (the round-1 report suggested this; it is not yet applied).
- Bystander filter: extend to "asking for my (mom|dad|sister|brother|friend|gf|bf|wife|husband|partner)" and to posts whose body third-person subject "rejected/decided/did" the title action.
- Jargon filter: add plural forms NTAs/YTAs/ESHs and "the sub/this sub" meta posts.
- Action-coherence check: when the stripped closing question introduced the only mention of the action's object (scr_b47j4w "friend"), the action noun never appears in the situation; a cheap check "action head noun (friend/phone/gift/...) absent from situation and situation ends in 'So...' / ':'" would catch it.
- Dropped-I agreement: when "I" is deleted from a coordinated clause ("and was thinking"), apply was->were there too (currently only after an explicit "you").
```

## 报告 2

```
JUDGE REPORT — source aita_berkeley, round 2 (seed 20261006; 46 rows = the entire 50-family WIBTA source minus the 4 rows judged in round 1; judged by hand, no API)
Sheet saved in place: /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_aita_berkeley.csv (same 11 columns, same row order, csv QUOTE_ALL; every row filled; 20 rows carry a note, all notes are "pass; ..." observations).

PASS RATES (n=46)
- pass_second_person: 46/46 (100%)
- pass_two_exclusive_actions: 46/46 (100%)
- pass_no_verdict_in_situation: 46/46 (100%)
- all three jointly: 46/46 (100%)
Round 1 for comparison: 42 / 89 / 62 / joint 20 (n=100, incl. retrospective waves). All three columns clear the >= 90% gate. Caveat: n=46, so the 90% gate is met with a one-sided 95% lower bound of ~92%; the source is small (50 families) because the residual-plural hard flag dropped 446/539 WIBTA posts.

POLICY APPLIED (same as round 1, strict version)
- second_person = 0 for ANY residual I/me/my/we/our/us/ourselves referring to the decision-maker (no "minor" tolerance this round) or for quoted first-person speech rewritten to "you". Regex scan over situation + both actions confirms zero such tokens in all 46 rows (the only "am" hits are clock times "530 am" / "7 am"). Quoted spans ("freak her out", "they smell", "you know how they are, you need to hide your stuff better", "destroy his future", "dirt", "having a teenage attitude", "Also, just a friendly Venmo reminder!", "children call the person who takes care of them most mama") are all either third-person paraphrase or genuine second-person addressed to the narrator, so speakers are recoverable.
- two_exclusive_actions = 0 if either action is not a grammatical imperative or the pair is not a mutually exclusive choice for one decision. All 46 pairs are "Do X / Do not X" with a base-form verb head; no coordinated gerunds, no leading object pronouns, no "To ..." heads, no NPIs left in the affirmative.
- no_verdict = 0 for AITA jargon (none found: no TA/AH/NTA/YTA/ESH/NAH/asshole/TL;DR) or for a completed one-shot deed with narrated aftermath. All 46 are WIBTA posts narrating a live decision ("you're thinking about...", "you want to tell...", "you plan on..."); two rows have a prior step already taken but the decision is still open (bk_10k1k6x confrontation happened, whether to keep paying is live; bk_109a1bq device removed once, mom reinstalled it) — passed without needing the "retrospective" label.

FAILURE PATTERNS
None in any column. Residual imperfections that did NOT fail a column (noted on the sheet), with 3 examples each:
1. Meta/preamble residue without first person, not caught by the meta filter: bk_10kbhka ("Please excuse the comparatively boring dilemma, but you're torn right now"), bk_11otjd4 ("Trying to keep some things simple for privacy reasons So you (teensF) ..."), bk_zqopy8 ("You'll sum up some of his claims here;"); also bk_10lyynr ("the family you're asking about here"), bk_10p7omc ("Like you said").
2. Age-tag / punctuation residue: bk_11sqedm ("You (34 nb)", "B. Has kept"), bk_120u368 ("So you 21, babysat"), bk_10egfdw ("Then..each").
3. Title wording that is vague or carries a dangling adverbial, still grammatical and exclusive: bk_z8d39l ("Make fruit preserves for your BIL because last Christmas he said your gifts are tacky"), bk_z4kw98 ("Report your brother" — to whom unstated), bk_11otjd4 ("Tell someone you couldn't babysit"); also bk_101sa20 ("Decide to sue your friend"), bk_yxqp92 ("Do not help your adopted kid any more" / "Help your adopted kid" — NPI correctly dropped from the affirmative).
4. Source-text defects passed through verbatim (not conversion bugs; verified against the raw CSV): bk_107j5ko ("You're the confirmation email ..." = source "I'm" typo for "In"), bk_yv601t ("You told explained" = source "I told explained"), bk_z4cpj3 ("you you didn't" = source "I I didn't"); also bk_zg3y6i ("they were displaying" with no antecedent in the source), bk_ysepnu ("send Late").

REMAINING CONVERSION BUGS (verified against the HF source CSV)
1. Meta-sentence removal cuts mid-sentence when the meta phrase is coordinated: bk_10426bp source "I'll keep it short and sweet. I (30f) and my wife ..." -> situation opens "And sweet. You and your wife are expecting ..." The matched span "I'll keep it short" is removed but the coordinated tail survives and is capitalised. Fix: when a meta regex matches, delete to the sentence boundary, not to the match end; and extend opens_mid_stream to a leading bare coordinator ("And"/"But"/"So" + fragment under ~3 words).
2. Meta-sentence removal deletes a content-bearing sentence when the meta preamble is a prefix: bk_101sa20 source "To make this short and sweet I used to run an OF." is dropped entirely, so "decided to call it quits" and "your photos" lose their referent. Fix: strip only the preamble prefix ("To make this short( and sweet)?,?") and keep the main clause when the remainder has a subject+verb; same for "Long story short, ...", "Background: ...".
3. First-person-free meta residue is not filtered: "Please excuse the ... dilemma", "Trying to keep ... simple for privacy reasons", "You'll sum up ... here", "the family you're asking about here", "Like you said", "Background your SIL ..." (bk_10ji37a), "First some backstory:" (bk_yuzqzy). These are harmless for the three gate columns but add a few words of noise; a small regex list (excuse the|privacy reasons|sum up|asking about here|like you said|^Background:?|^First some backstory:?) would clean them.
4. Paragraph joins without terminal punctuation merge a meta line into the first sentence (bk_11otjd4 "privacy reasons So you (teensF) have"); the cleaner should insert a period when joining a line that lacks one. Also a stray backslash survives ("\2 days", bk_11otjd4) and age tags inside parentheses with non-standard genders ("(34 nb)", "(teensF)") or without parentheses ("you 21,") escape age_tag_removed.
5. Abbreviation-aware sentence splitting: "working with B. For about 9 months ... B. Has kept bugging you" (bk_11sqedm) — single-letter initials followed by a period are treated as sentence ends and the next word is capitalised.
6. Minor: the "because ..." clause of a negated WIBTA title is kept on both polarities (bk_z8d39l); truncating the affirmative at the subordinator (as the ETHICS VP already does at ", because/since") would read better. No pair failed on it.

No situation/action text was edited. Scratch: none kept (sheet written directly). Raw source consulted at /Users/yuansir/.cache/huggingface/hub/datasets--ucberkeley-dlab--normative_evaluation_llms_everyday_dilemmas/snapshots/d2f0cc01f5fef9e56dee7101d523eaaae484233a/normative_evaluation_everyday_dilemmas_dataset.csv (read-only).
```

## 报告 3

```
JUDGE REPORT — source moral_stories, round 2 (seed 20261006; 100/100 rows read and judged by hand, no API)
Sheet saved in place: /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_moral_stories.csv (same 11 columns, same row order, csv QUOTE_ALL; every 0 has a note; "minor:" notes on passes). Untouched pre-judgement copy: /private/tmp/claude-501/-Users-yuansir-workspace-CS329X-Project/64062123-fa10-4af6-86b2-26906e1a925d/scratchpad/ms_r2_backup.csv

PASS RATES (gate: each column >= 90%)
- pass_second_person: 79/100 (round 1: 75) -> FAILS gate
- pass_two_exclusive_actions: 96/100 (round 1: 94) -> passes
- pass_no_verdict_in_situation: 100/100 (round 1: 100) -> passes
- all three jointly: 76/100 (round 1: 71)
- by wave: wave 1 n=7: P2 5, joint 4; 2a n=32: P2 28, joint 26; reserve n=61: P2 46, joint 46
- needs_review=pronoun_same_gender_other: 18 rows, only 4 pass P2 (14 fail). Unflagged 82 rows: P2 75/82 = 91.5%, joint 72/82 = 87.8%. Making this flag HARD (as the plan says if round 2 fails) lifts P2 over the gate; the joint rate then hinges on the 3 action fails + 7 remaining P2 fails below.

POLICY (same as round 1, applied strictly): any 3rd-person pronoun/possessive denoting the decision-maker in situation OR action = P2 0; they/their for you+someone = P2 0; the other party's pronoun over-replaced by "you" = P2 0; garbled possessive for the actor ("yours in-laws") = P2 0; a single coordinated 3sg verb slip = pass with "minor" note; >=2 slips, non-imperative or unintelligible action, or identical actions = actions 0. No situation leaked a verdict or a completed deed (Moral Stories situation+intention is pre-decision by construction).

FAILURE PATTERNS (most common first)
1. Actor's he/his/him/she/her left in 3rd person when another same-gender person is in the clause — 11 rows, all carry pronoun_same_gender_other: ms_3XCC1ODXDM9LRCQTK8UI6TW8BPZRQZ ("chocolates that he had won at work and his wife Anne"), ms_3907X2AHF13JNG8T550S5GYQT75P2A ("Bill who asks him if he can spare"; actions "he does have some change he can give him"), ms_38BQUHLA9XYR9K0L0N6XVP7YP65OMW ("You have a niece she loves", "her niece's tuition"); also ms_39LNWE0K4VU0Q6URBUKE22S6RTDIUC, ms_3TGOYF991YK5ZXPR5B9SL5GHJOEUU8, ms_3YDTZAI2WYEQ924EOH8QXZDQARF419, ms_3RGU30DZTB6D899OKAESNTQCQ6MJMN, ms_3SNVL38CI5QVA73FP6KQLCLDCXMCKY, ms_3300DTYQT3FWI8LOY2AI7MXPW6CEQO, ms_39DD6S19JQ95W0MFLYTVYF9T11EZE4, ms_37TD41K0AI7TYQGNUFTSCYCNSJBCSA.
2. Over-replacement: the OTHER party's pronoun rewritten to "you" — 6 rows: ms_3K3R2QNK8C17F51O70E1P9T39YFU9L ("congratulate you and asks to do another activity you may beat you in" — also actions fail, unintelligible), ms_3XIQGXAUMD6VIQ7QX8R4VK118JZX7H ("you can't stand being around you"), ms_3M68NM076I5SHU795ZGK0OFHAA16R2 ("walk with the visitor ..., guiding you to the right places"); also ms_3300DTYQT3FWI8LOY2AI7MXPW6CEQO ("Ken is talking with his friend you and tells you that you recently tried to kill yourself"), ms_39O5D9O87UQPE9V840SR4Q4B02GC3K ("Tell max that you should definitely pick whatever sport you're drawn to"), ms_3U8YCDAGXQEXRI6UQVB3MXVL179Q0O ("pretend to try and swipe at you" = the cat). 3 of these are unflagged.
3. Plural they/their referring to actor+other survived the new plural_refers_to_actor flag — 4 rows: ms_3VA45EW49OLUDVEW71NZBXJVSHO1OO (actions: "and they drive there" / "Tell your son that they are driving"), ms_3KXIR214I5EXYNMA7L842INV4K242B ("the walls of their home" after "You are telling Jane"), ms_35H6S234SBY3C79B8S3HXNALJCG56W (action "introduce new excitement into their relationship"); also ms_37TD41K0AI7TYQGNUFTSCYCNSJBCSA ("an argument they left unresolved"). None has a "you and X" construction, which is why the heuristic missed them; row 1 has they inside the actions, which the fix report said would hard-drop — it did not.
4. Garbled actor possessive "yours" + noun — 2 rows: ms_3W8CV64QJ3X2AJV471726U4DDLKH92 ("dinner with yours in-laws", x4 incl. both actions), ms_3SKEMFQBZ43TY4D28U4LJQPUMTUK83 ("this is yours last day"). Looks like possessive "her" mapped to "yours" when the following token is not tagged as a noun ("in-laws", "last").
5. Broken action pairs — 4 rows (3 unflagged): ms_3I2PTA7R3USZ48DYUOLL5HAUH0JKQK ("Go inside because you are doesn't know where the dog has been and just waits inside"; two agreement slips), ms_354P56DE9L1NM9LR3YLHWCK9SGQS7K ("Be having a picnic at the park, and you leave your trash on the ground"; not an imperative — "is having" imperativised to "Be having"), ms_3JC6VJ2SACH4Z9LEY5KTDSC7EC1A5J (X "Ask for a number 6 xor [exclusive or] a number 9" vs Y "Ask for a number 6 or a number 9": identical, source noise), ms_3K3R2QNK8C17F51O70E1P9T39YFU9L (pattern 2).
6. Contraction 's mis-mapped to 've — 2 rows, noted not failed on their own: ms_3KXIR214I5EXYNMA7L842INV4K242B ("you've done with her entirely" = you're done), ms_3907X2AHF13JNG8T550S5GYQT75P2A ("you've approached by a homeless man" = you're approached).
7. Single coordinated 3sg verb slips, passed with "minor" — 13 rows: ms_3T3IWE1XG7LY7R3LOXZD68XQY2NTQO ("and grabs it"), ms_32RIADZIST2Q3M3810NAT00Z0LF4S4 ("then tucks him in"), ms_3M0NZ3JDP2W50HTMAX0SUL3GPJJZ5U ("before you has to meet"); also rows 1 13 19 29 38 50 67 77 84 90 92. Appositive/relative agreement: ms_39OWYR0EPLPXXOC6KNBI2QLR8B7FY0 ("You, who lives with your housemate Paul ... get back at your Brandon"), ms_3BF51CHDTW8KEP7R75O9DJ3KAM6H0G ("You, who is white").
8. Garbled situations from name/pronoun deletion (noted): ms_3RGU30DZTB6D899OKAESNTQCQ6MJMN ("you see necklace loves out of your price range"), ms_39O5D9O87UQPE9V840SR4Q4B02GC3K ("You who is a giant hockey fan is watching your son Max is contemplate"), ms_3U8YCDAGXQEXRI6UQVB3MXVL179Q0O ("Jeff's friend you who has come to visit").

REMAINING CONVERSION BUGS / RULE FIXES
- (1) pronoun_same_gender_other must become a HARD flag: 14/18 flagged rows fail P2 in round 2 (13/16 in round 1). This alone takes P2 to ~91.5% on this sample.
- (2) Over-replacement is the main unflagged P2 leak (3 unflagged rows). The lexical rule maps every same-gender pronoun to "you" even when its antecedent is the nearest other mention (the visitor, the cat "it", Max, Fred as object of "being around"). Cheap fix: when the actor's name appears as an object/appositive ("his friend <Actor>", "<Other> ... around <Actor>") or an "it" follows a non-human noun, do not map; or hard-flag rows where the converted text contains "you ... you" inside one clause with a transitive verb ("congratulate you and ... beat you", "swipe at you", "guiding you").
- (3) plural_refers_to_actor misses they/their with no "you and X" trigger: extend the heuristic to any they/their/them whose nearest preceding plural antecedent is absent (rows 1, 28, 79, 100 all have only singular nouns before the pronoun), and make the "any they/their within the actions" branch actually fire (row 1 slipped through).
- (4) Possessive "her/his" -> "yours" when followed by a hyphenated or adjective-like token ("in-laws", "last"): map determiner-position her/his -> "your" regardless of the next token's tag; "yours" should only replace standalone "hers/his".
- (5) Contraction "<Name>'s" meaning "is" -> "you've": map 's -> "you're" when followed by a participle/adjective/adverb ("'s done", "'s approached"), "you've" only before a past participle with have-semantics is unsafe, so default to "you're".
- (6) Imperativiser turns progressive "is having" into "Be having": when the head is be + V-ing, lemmatise the V-ing instead ("Have a picnic").
- (7) Coordinated 3sg verb agreement is still only fixed on the head verb (13 minor slips + 1 fail): lemmatise VBZ tokens coordinated to the imperative head, and after "you" in the situation ("you has", "you are doesn't", "You, who lives/is").
- (8) Identical action pairs after noise removal (row 37): drop families where action_x == action_y after stripping bracketed insertions.
```

## 报告 4

```
JUDGE REPORT — source hendrycks_ethics, ROUND 2 (seed 20261006; 100 rows, all read and judged by hand, no API)
Sheet saved in place: /Users/yuansir/workspace/CS329X_Project/data/annotation/e2c_handcheck_hendrycks_ethics.csv (same 11 columns, same row order, csv QUOTE_ALL; untouched copy at /private/tmp/claude-501/-Users-yuansir-workspace-CS329X-Project/64062123-fa10-4af6-86b2-26906e1a925d/scratchpad/eth_r2_backup.csv). Waves in sheet: 1 = 21, 2b = 75, reserve = 4.

PASS RATES
- pass_second_person: 100/100 (1.00)
- pass_two_exclusive_actions: 100/100 (1.00)
- pass_no_verdict_in_situation: 100/100 (1.00)
- all three jointly: 100/100 (1.00) — source clears the >= 90% per-column gate (round 1: 94 / 97 / 98, joint 89).

POLICY APPLIED (same as round 1, strict): any residual I/me/my/we/our/us/am or converted quoted first-person speech = second_person 0; both actions must be grammatical imperatives forming exclusive alternatives for the same decision (VP / Do not VP); a reason that narrates the habit action as already done, or states a normative claim ("it's more important that ..."), = no_verdict 0. A regex sweep over situation + both actions confirms zero first-person tokens in all 100 rows; every action_y equals "Do not " + lower-cased action_x.

FAILURE PATTERNS
None. The round-1 failure patterns did not recur in this sample:
1. Residual we/our/us (6 rows in round 1) — 0 rows (the new residual_first_person_plural hard flag; e.g. round-1 eth_j_a8baef161758 / eth_j_037d6916aff7 / eth_j_f156385a6932 types are absent).
2. Broken VP: leading "to ", stative "become + adj", trailing ", because" clause / ".." — 0 rows.
3. Reason that pre-empts the verdict / narrates the completed deed — 0 rows. Closest case, passed with note: eth_j_17740c1bb347 ("it's way more satisfying to watch her twitch with discomfort" — a hedonic motivation, not a normative verdict).

INFORMATIONAL NOTES (22 rows passed with "info:" notes; all source-quality, not conversion errors)
- Antecedent/pronoun mismatch in the reason (plural noun + he/she, dangling he), 8 rows: eth_j_58771274d06e (children/she), eth_j_e36262c4746a (students'/he), eth_j_9fc16f643b3a (students'/he); also eth_j_054cb9f75663, eth_j_93f99509ca41, eth_j_f39c5caa30a6, eth_j_4fc7cbfb849c, eth_j_3a4d235f98d5.
- Source typos carried into actions, 5 rows: eth_j_94aa05433669 ("Provede" = provide; correctly carries head_verb_unknown — the only row where a reader must infer the verb), eth_j_a347136bd15b ("uncles dog"), eth_j_f36ac4cff2b7 ("captains ship"); also eth_j_633eb0b832c1 (stray comma), eth_j_7713eeda4791 ("kid's").
- Negation scope loose over "all" ("Do not go to all of your son's football games" is logically complementary but loose for a single game), 2 rows: eth_j_d639574debc3, eth_j_e36262c4746a.
- Garbled source tense/time, 4 rows: eth_j_c78ee4ac8fac ("Tonight, Susie was giving attitude yesterday"), eth_j_e9f7fe7f9ea2, eth_j_a25039d60a30, eth_j_971e2fd97c9c; source agreement error eth_j_cf73cf6b42a6 ("your son clean it"); capitalisation/apostrophe eth_j_7288bfacd42b, eth_j_9e000064c3a6.

REMAINING CONVERSION BUGS
No conversion bug produced a failure in this sample. Optional polish only:
1. head_verb_unknown rows (eth_j_94aa05433669 "provede") could be routed to needs_review or dropped if typo-free actions are wanted; current informational handling is defensible.
2. Habitual "when/whenever <clause>" retained in the VP (e.g. "Kiss your son good night when he goes to sleep", "Feed your neighbor's cat when he's at the hospital ...") is still kept; harmless for the x/y contrast but makes the action a standing policy rather than a one-off choice — same observation as round 1, not a failure.
3. Optional source-quality filter: drop reasons whose pronoun has no compatible antecedent (8% of rows) — reads sloppy but the decision-maker is unambiguous, so passed.
```

## 报告 5

```
VERIFIER REPORT — E2C handcheck round 2 (scruples 100, aita_berkeley 46, moral_stories 100, hendrycks_ethics 100)
Sample: numpy default_rng(20261006).choice(n, 25, replace=False) per sheet, judged blind (situation + actions only, judge columns hidden), then compared. Row indices (0-based): n=100 sheets -> [2,4,8,15,18,20,24,25,29,30,44,46,52,55,62,66,74,77,78,80,82,86,87,94,95]; aita_berkeley (n=46) -> [1,3,6,7,8,9,10,13,14,16,17,18,20,26,27,28,29,32,33,34,37,38,39,43,45]. Sheets were NOT modified. Full-sheet rates recomputed with pandas from the saved CSVs.

INTEGRITY CHECKS (all four sheets)
- situation text byte-identical to data/families/contested_pool.jsonl for every row; no duplicate family_ids; zero overlap with the round-1 judged family_ids (data/annotation/e2c_handcheck_round1/); every row with a 0 carries a non-empty note; pass columns contain only 0/1.
- Regex sweep for I/me/my/we/our/us/ourselves/am/Im/Ive/lemme/imo over situation + both actions: scruples hits = "1-2 am", "i.e.", German "im" (false positives) + "Lemme" (scr_a5o2t7) and "imo" (scr_akt8eq), both already failed by the judge; aita_berkeley hits = clock times "530 am" / "7 am" only; moral_stories and hendrycks_ethics = none.

TABLE (full sheet; agreement = my blind verdict vs judge on the 25 sampled rows, per column sp/act/nv and on the joint all-three verdict)

source           | n   | pass_second_person | pass_two_exclusive_actions | pass_no_verdict | joint pass | agreement on 25 (sp/act/nv/joint) | gate (>=90% per column)
scruples         | 100 | 95                 | 96                         | 98              | 90         | 25/25/25/25                       | PASS / PASS / PASS  -> PASS (joint 90)
aita_berkeley    | 46  | 46 (100%)          | 46 (100%)                  | 46 (100%)       | 46 (100%)  | 25/25/25/25                       | PASS / PASS / PASS  -> PASS (n=46: one-sided 95% lower bound ~93.7%)
moral_stories    | 100 | 79                 | 96                         | 100             | 76         | 25/25/25/25                       | FAIL / PASS / PASS  -> FAIL (second person)
hendrycks_ethics | 100 | 100                | 100                        | 100             | 100        | 25/25/25/25                       | PASS / PASS / PASS  -> PASS

DISAGREEMENTS: none. My blind verdicts matched the judge on every sampled row and column.
- scruples sampled fails I reproduced independently: scr_a6t0nc sp=0 (sister's unquoted "I'll be able to pay you back" -> "you'll be able to pay you back"), scr_a5o2t7 sp=0 ("Lemme"), scr_b47j4w act=0 (actions about a friend the situation never mentions; situation ends "So..."), scr_a3rv3h act=0 ("Go and got vaccinating"), scr_at602v act=0 (self-contradictory " but " title pair), scr_b9lft7 act=0 + nv=0 ("Asking for your mom...", "She rejected the job request", non-imperative action), scr_a9wrpl nv=0 ("NTAs or YTAs", meta post about the subreddit). The other 18 sampled rows pass on all three columns; I also saw the judge's informational observations (scr_b9joc7 "Pretty much this -", scr_alnb0z dangling "he", scr_auchy8 "and was thinking", scr_b4rb8y "brought these children's") and agree none fails a column.
- aita_berkeley: all 25 pass. Quoted spans in the sample ("freak her out", "they smell", "you know how they are, you need to hide your stuff better", "Also, just a friendly Venmo reminder!") are third-person paraphrase or genuine second person; bk_10426bp opens "And sweet." (meta cut mid-sentence) and bk_120u368 "So you 21, babysat" are noise, not column failures; bk_10k1k6x and bk_107j5ko have a prior step taken but a live decision.
- moral_stories sampled fails I reproduced independently: ms_3YDTZAI2WYEQ924EOH8QXZDQARF419 sp=0 (actor's "her" left in both actions, flagged pronoun_same_gender_other), ms_39O5D9O87UQPE9V840SR4Q4B02GC3K sp=0 (Max's "he" -> "you"; garbled "You who is ... is watching your son Max is contemplate"), ms_35H6S234SBY3C79B8S3HXNALJCG56W sp=0 ("their relationship" = you + girl, unflagged), ms_3M68NM076I5SHU795ZGK0OFHAA16R2 sp=0 ("guiding you" = the visitor, unflagged), ms_3U8YCDAGXQEXRI6UQVB3MXVL179Q0O sp=0 ("swipe at you" = the cat; "Jeff's friend you who has come to visit"), ms_3I2PTA7R3USZ48DYUOLL5HAUH0JKQK act=0 ("because you are doesn't know ... and just waits inside", two slips). Single-slip rows (ms_32RIADZIST... "then tucks him in", ms_3M0NZ3JDP2... "you has to meet", ms_3S4AW7T80... "and leaves") passed as "minor", consistent with the judge's policy. 3 of the 5 sp fails in my sample are UNFLAGGED, which confirms that making pronoun_same_gender_other HARD is necessary but not sufficient.
- hendrycks_ethics: all 25 pass; eth_j_94aa05433669 "Provede" (source typo, head_verb_unknown), eth_j_d639574debc3 loose "all of" negation scope, eth_j_e36262c4746a / eth_j_3a4d235f98d5 dangling "he" in the reason, eth_j_94f02106c66b "Today, she broke the coffee pot last night" are source defects that do not fail a column.

MORAL STORIES BREAKDOWN (full sheet)
- needs_review contains pronoun_same_gender_other: 18 rows, sp pass 4/18. Unflagged: 82 rows, sp 75/82 = 91.5%, act 79/82, joint 72/82 = 87.8%.
- By wave: 1 (n=7) joint 4; 2a (n=32) joint 26; reserve (n=61) joint 46.
- In the pool the flag sits on wave 1 134/600, 2a 525/2,424, reserve 1,016/4,746; hard-dropping it leaves 1,899 unflagged 2a families to refill wave 1 to 600 and shrinks moral_stories 7,770 -> ~6,095.
- The 7 unflagged sp fails split into 3 over-replacements of another party's pronoun (visitor / cat "it" / Max / "being around Fred") and 4 they/their for you+other with no "you and X" trigger (one of them inside the actions, which the fix report said would hard-drop but did not). On this sample a hard flag alone gives 91.5% with a 95% lower bound well under 90% (binomial, n=82), so the gate would be met only nominally; the over-replacement and plural heuristics have to be fixed too.

GATE VERDICT
- scruples: PASS (95 / 96 / 98; joint 90). aita_berkeley: PASS (100 / 100 / 100 on the whole remaining source). hendrycks_ethics: PASS (100 / 100 / 100).
- moral_stories: FAIL on pass_second_person (79%); the other two columns pass.

RECOMMENDATION
1. Do not screen moral_stories yet. Fix in load_contested_sources.py: pronoun_same_gender_other -> HARD_FLAGS; extend plural_refers_to_actor to any they/their/them with no plural antecedent and make the in-action branch fire; block over-replacement when the actor's name is an object/appositive or the pronoun is "it" after a non-human noun (or hard-flag "you ... you" in one transitive clause); determiner her/his -> "your" (never "yours"); "<Name>'s" -> "you're" by default; be + V-ing -> lemmatised V; lemmatise VBZ coordinated to the imperative head and after "you"; drop x == y after stripping brackets. Rebuild (scripts/16), regenerate the moral_stories sheet only with a new seed (round 3, 100 rows, exclude rounds 1 and 2), re-judge.
2. Paid screening (tasks/e2c_plan.md section 11 step D) CAN start now for the three passing sources plus mc_low, provided the section 9 commit precondition is met: filter data/prompts/contested_pool_T1.jsonl to source != moral_stories (675 + 585 + 50 + 300 = 1,610 families, 3,220 T1 prompts, 9,660 calls, ~$13) and run 04_query_teachers.py on that file; append the moral_stories wave-1 prompts (600 families, 1,200 prompts) to the same --out files once round 3 passes. The screening cache makes this split free of rework. Expect only ~290-490 new contested families from the Reddit + ETHICS part, so the 2a/2b triggers in section 1 will almost certainly fire.
3. Optional scruples polish (not required for the gate): unquoted reported speech after "saying / like yeah / responds back:", idiom list + lemme/imo/imho/afaik, drop titles containing " but ", bystander filter for "asking for my <relative>", plural jargon NTAs/YTAs, coordinated-verb base-form check ("Go and got").

Scratch: /private/tmp/claude-501/-Users-yuansir-workspace-CS329X-Project/64062123-fa10-4af6-86b2-26906e1a925d/scratchpad/verify2/ (blind dumps per source, index lists, verify.py). Sheets unchanged.
```
