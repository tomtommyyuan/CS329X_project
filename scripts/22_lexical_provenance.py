"""Step 22: E7 lexical-provenance baseline on the TRAINING TEXTS (tasks/e7_plan.md §1 last row, §4 last paragraph)
-> {out}/lexical_accuracy.csv, lexical_confusion.csv, lexical_features.csv, lexical_cue_survival.csv, lexical_inventory.csv, lexical_run_info.json, lexical_summary.md.

Examples
  python scripts/22_lexical_provenance.py --sets original,contested --sft-dirs data/sft_paired,data/sft_e2c_paired --out results/e7_lexical --seed 0 --hash-bits 18
  # one set, numpy backend (no scikit-learn), smaller hash space
  python scripts/22_lexical_provenance.py --sets original --sft-dirs data/sft_paired --out /tmp/e7_lex --backend numpy --hash-bits 16
  # synthetic tree (tests): explicit teachers
  python scripts/22_lexical_provenance.py --sets synth --sft-dirs /tmp/sft --teachers alpha,beta,gamma --out /tmp/e7_lex --n-folds 3 --hash-bits 12 --min-df 5

Question: can a purely lexical / stylistic classifier identify which teacher wrote a demonstration, and does that cue survive
the F / C register rewriting? Inputs are the paired SFT files {sft_dir}/{teacher}_{O|F|C}_s1.jsonl (seed 1 only; the other
seeds differ in row order); text = the rationale of `text_target`. No API, no GPU, no model download. The student checkpoints
were deleted, so (unlike docs/03's original E7 design) the lexical baseline is run on the training texts, not on student output.

Features and classifier are fixed in vcd.analysis.lexical_provenance (hashed char 3-5-grams + word uni / bigrams, TF, L2 per
block, 2**hash_bits buckets per block; multinomial L2 logistic regression, C = 1, balanced class weights; length-only control
= n_words, n_sentences, mean_word_len). No tuning on test folds. PoS n-grams are added only if a tagger is importable offline;
none is in this venv, so they are skipped (recorded in lexical_run_info.json).

Evaluations, per set, each per teacher with Wilson 95% CIs + macro (balanced) accuracy + pooled accuracy, chance = 1/3:
  within_O / within_F / within_C   5-fold CV with folds grouped by family_id (a held-out family is never seen in training)
  O->F, O->C                       same_prompts (train on all O, test on F / C of the same prompts; the brief's design) and
                                   family_disjoint (fold models of within_O applied to the F / C texts of the held-out families)
  F+C->O                           reverse, same_prompts and family_disjoint (descriptive)
  the same grid with the length-only features; nearest O-style centroid (cosine) of F / C texts (and O, cross-fold)
Plus the top-k word features per teacher of the O / F / C models with their rates per 1,000 tokens in the teacher's own
O / F / C texts and in the other teachers' texts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from vcd.analysis import lexical_provenance as LP


def _md_table(df: pd.DataFrame, cols: list[str], rename: dict | None = None) -> list[str]:
    rename = rename or {}
    lines = ["| " + " | ".join(rename.get(c, c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                cells.append("—" if np.isnan(v) else (f"{v:.3f}" if abs(v) < 100 else f"{v:,.1f}"))
            elif isinstance(v, (bool, np.bool_)):
                cells.append("yes" if v else "no")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _macro(acc: pd.DataFrame, set_name: str, features: str, evaluation: str, overlap: str) -> tuple[float, float, float]:
    m = acc[(acc["set"] == set_name) & (acc.features == features) & (acc.evaluation == evaluation) & (acc.overlap == overlap) & (acc.teacher == "macro")]
    if m.empty:
        return np.nan, np.nan, np.nan
    r = m.iloc[0]
    return float(r.acc), float(r.ci_lo), float(r.ci_hi)


def headline(acc: pd.DataFrame, sets: list[str], o: str, rew: list[str]) -> str:
    """Chinese one-paragraph reading of the numbers (facts only; the qualitative words follow fixed comparisons with chance)."""
    parts = []
    for s in sets:
        w = _macro(acc, s, "ngram", f"within_{o}", "family_disjoint_cv")
        tr = {u: _macro(acc, s, "ngram", f"{o}->{u}", "family_disjoint") for u in rew}
        tr_same = {u: _macro(acc, s, "ngram", f"{o}->{u}", "same_prompts") for u in rew}
        wi = {u: _macro(acc, s, "ngram", f"within_{u}", "family_disjoint_cv") for u in rew}
        ln = _macro(acc, s, "length", f"within_{o}", "family_disjoint_cv")
        ln_tr = {u: _macro(acc, s, "length", f"{o}->{u}", "family_disjoint") for u in rew}
        survive = [u for u in rew if tr[u][1] > LP.CHANCE + 0.10]
        verdict = "词汇线索**大部分穿过**改写" if len(survive) == len(rew) else ("词汇线索部分穿过改写" if survive else "词汇线索在改写后降到随机水平附近")
        parts.append(
            f"**{s}**：{o} 内 5 折（family 分组）三分类 macro 准确率 {w[0]:.3f} [{w[1]:.3f}, {w[2]:.3f}]（chance 0.333）；"
            f"{o} 训练→" + " / ".join(f"{u} 测试 {tr[u][0]:.3f} [{tr[u][1]:.3f}, {tr[u][2]:.3f}]" for u in rew) + "（family 不相交；同题版 "
            + " / ".join(f"{tr_same[u][0]:.3f}" for u in rew) + "）；" + " / ".join(f"{u} 内 {wi[u][0]:.3f}" for u in rew)
            + f"。只用长度（词数、句数、平均词长）：{o} 内 {ln[0]:.3f}，{o}→" + " / ".join(f"{u} {ln_tr[u][0]:.3f}" for u in rew) + f"。判读：{verdict}。"
        )
    return "\n\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sets", default="original,contested", help="comma list of set names (same length as --sft-dirs)")
    ap.add_argument("--sft-dirs", default="data/sft_paired,data/sft_e2c_paired", help="comma list of dirs with {teacher}_{O|F|C}_s{sft_seed}.jsonl")
    ap.add_argument("--out", default="results/e7_lexical")
    ap.add_argument("--teachers", default=",".join(LP.TEACHERS), help="comma list of teacher keys (classes)")
    ap.add_argument("--styles", default=",".join(LP.STYLES), help="comma list; the first is the original style, the others its rewrites")
    ap.add_argument("--sft-seed", type=int, default=1, help="seed suffix of the SFT files to read (seeds differ in row order only)")
    ap.add_argument("--seed", type=int, default=0, help="seed of the hashing and of the family folds")
    ap.add_argument("--hash-bits", type=int, default=18, help="2**hash_bits buckets per feature block (characters, words)")
    ap.add_argument("--n-folds", type=int, default=5)
    ap.add_argument("--C", type=float, default=LP.DEFAULT_C, help="inverse L2 strength of the logistic regression (fixed; not tuned)")
    ap.add_argument("--max-iter", type=int, default=LP.DEFAULT_MAX_ITER)
    ap.add_argument("--backend", default="auto", choices=["auto", "sklearn", "numpy"], help="logistic-regression solver")
    ap.add_argument("--top-k", type=int, default=20, help="discriminative word features per teacher and model style")
    ap.add_argument("--min-df", type=int, default=20, help="a word feature is named only if it occurs in >= this many texts of the model style")
    args = ap.parse_args()

    sets = [s.strip() for s in args.sets.split(",") if s.strip()]
    dirs = [Path(d.strip()) for d in args.sft_dirs.split(",") if d.strip()]
    if len(sets) != len(dirs):
        sys.exit(f"--sets ({len(sets)}) and --sft-dirs ({len(dirs)}) must have the same length")
    teachers = tuple(t.strip() for t in args.teachers.split(",") if t.strip())
    styles = tuple(s.strip() for s in args.styles.split(",") if s.strip())
    o, rew = styles[0], list(styles[1:])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()
    tagger = LP.pos_tagger_available()
    log = lambda *a: print(*a, flush=True)  # noqa: E731

    acc_frames, conf_frames, feat_frames, inv_frames, set_info = [], [], [], [], {}
    for set_name, sft_dir in zip(sets, dirs):
        df = LP.load_sft_texts(sft_dir, teachers=teachers, styles=styles, seed=args.sft_seed)
        inv = LP.inventory(df, teachers=teachers, styles=styles)
        inv.insert(0, "set", set_name)
        inv_frames.append(inv)
        log(f"[{set_name}] {sft_dir}: {len(df)} texts; paired = {inv.paired.tolist()}")
        fz = LP.HashedFeaturizer(hash_bits=args.hash_bits, seed=args.seed)
        res = LP.run_evaluations(df, set_name, fz, n_folds=args.n_folds, seed=args.seed, C=args.C, backend=args.backend, max_iter=args.max_iter, teachers=teachers, styles=styles, log=log)
        acc_frames.append(res.accuracy)
        conf_frames.append(res.confusion)
        for s in styles:
            key = f"{s}_full"
            if key in res.models:
                feat_frames.append(LP.top_word_features(res.models[key], fz, df, s, set_name, k=args.top_k, min_df=args.min_df, teachers=teachers, styles=styles))
        files = {f"{t}_{s}_s{args.sft_seed}.jsonl": _sha256(sft_dir / f"{t}_{s}_s{args.sft_seed}.jsonl") for t in teachers for s in styles}
        set_info[set_name] = dict(sft_dir=str(sft_dir), files_sha256=files, **res.info)
        log(f"[{set_name}] done in {res.info['runtime_s']:.1f}s")

    acc = pd.concat(acc_frames, ignore_index=True)
    conf = pd.concat(conf_frames, ignore_index=True)
    feats = pd.concat(feat_frames, ignore_index=True) if feat_frames else pd.DataFrame()
    inv = pd.concat(inv_frames, ignore_index=True)
    acc.to_csv(out / "lexical_accuracy.csv", index=False)
    conf.to_csv(out / "lexical_confusion.csv", index=False)
    feats.to_csv(out / "lexical_features.csv", index=False)
    (LP.cue_survival(feats, o, rew, k=args.top_k) if not feats.empty else pd.DataFrame()).to_csv(out / "lexical_cue_survival.csv", index=False)
    inv.to_csv(out / "lexical_inventory.csv", index=False)
    try:
        import sklearn

        skl = sklearn.__version__
    except ImportError:
        skl = None
    info = dict(sets=set_info, teachers=list(teachers), styles=list(styles), sft_seed=args.sft_seed, seed=args.seed, hash_bits=args.hash_bits, n_folds=args.n_folds, C=args.C, max_iter=args.max_iter, backend_requested=args.backend,
                top_k=args.top_k, min_df=args.min_df, pos_tagger=tagger, pos_features="skipped (no offline tagger)" if tagger is None else f"available: {tagger} (not used)", sklearn_version=skl, numpy_version=np.__version__,
                python=platform.python_version(), total_runtime_s=time.time() - t_start, command=" ".join(sys.argv))
    (out / "lexical_run_info.json").write_text(json.dumps(info, indent=2, default=str), encoding="utf-8")

    # ----- summary.md
    wide = LP.accuracy_table(acc, teachers)
    tcols = [*teachers, "macro", "pooled", "n"]
    L = [f"# E7 词汇溯源 baseline（训练文本的 teacher 三分类；tasks/e7_plan.md §1 末行、§4 末段；自动生成）", "",
         f"对象：每个 teacher 的 paired SFT 文件（seed {args.sft_seed}）的 rationale 文本，{' / '.join(styles)} 三种版本；标签 = 文件的 teacher。"
         f"特征：hashed 字符 3–5-gram + 词 uni / bigram（TF，分块 L2，每块 2^{args.hash_bits} 桶）；分类器：L2 多项 logistic 回归（C = {args.C}，balanced class weight，{set_info[sets[0]]['backend']}）；"
         f"长度对照只用词数、句数、平均词长。折叠按 family 分组（held-out family 不进训练）。chance = 1/3。macro = 三个 teacher 准确率的均值（CI 为正态近似），pooled = 全体准确率（Wilson）。"
         + ("PoS 3-gram **未做**：venv 里没有可离线使用的 tagger（不下载）。" if tagger is None else f"PoS tagger {tagger} 可用但未使用。"), "",
         "## 结论", "", headline(acc, sets, o, rew), "",
         f"预注册预测（tasks/e7_plan.md §4 末段）：{o} 内近 100%，F / C 上大幅下降。检验读数 = 下表 `family_disjoint` 的 {o}→F / {o}→C 行；本脚本的固定判读规则：所有 rewrite 版本的 macro CI 下界都 > 1/3 + 0.10 → “大部分穿过”，都 ≤ → “降到随机水平附近”，否则“部分穿过”。", "",
         "说明：`same_prompts` 行（O 训练、同一批题的 F / C 测试，即 brief 的设计）会被**内容记忆**抬高（改写保留理由与选择）；`family_disjoint` 行用 within_O 的 5 个折模型去认 held-out family 的 F / C 文本，只剩风格 / 用词偏好，是更干净的“词汇线索是否穿过改写”读数。"
         "F+C→O 为描述性反向行。本 baseline 的对象是训练文本而不是学生输出（checkpoint 已删，e7_plan §6），与行为溯源只能定性对比。", ""]
    L += ["## 数据", ""] + _md_table(inv, ["set", "teacher", *[f"n_{s}" for s in styles], "paired", "n_families", "prompt_overlap_all", "sources", *[f"mean_words_{s}" for s in styles]]) + ["", "`prompt_overlap_all` = 该 teacher 的 prompt 中三家都答了的比例；contested 集三家的题集只部分重叠，题材分布本身可能带 teacher 信息（family 分组折叠不能消除）。", ""]
    for feats_name, title in (("ngram", "## 词汇分类器（字符 n-gram + 词 n-gram）"), ("length", "## 长度对照（词数、句数、平均词长）"), ("ngram_centroid", "## 最近 O 风格质心（cosine）：判为自己 teacher 的比例")):
        sub = wide[wide.features == feats_name]
        if sub.empty:
            continue
        L += [title, ""] + _md_table(sub, ["set", "evaluation", "train", "test", "overlap", *tcols]) + [""]
    if not feats.empty:
        L += ["## 最有区分力的词特征（模型系数最大的词 / bigram；rate = 每 1,000 词 token 的出现次数）", "",
              f"`rate_{o}_own` / `rate_F_own` / `rate_C_own` = 该 teacher 自己 O / F / C 文本里的频率，`rate_{{style}}_others` = 其他两个 teacher 在该模型版本文本里的频率；`collision` = 该 hash 桶里还有其他常见词（列出，`|` 分隔）。O 模型列前 {args.top_k}，F / C 模型列前 10（完整表在 lexical_features.csv）。", ""]
        surv = LP.cue_survival(feats, o, rew, k=args.top_k)
        L += [f"### {o} 模型前 {args.top_k} 个线索在 F / C 中的去留（rate 保持 ≥ O 的一半算保留）", ""] + _md_table(surv, ["set", "teacher", "n", *[c for u in rew for c in (f"kept_{u}", f"removed_{u}")]]) + [""]
        for set_name in sets:
            for s in styles:
                for t in teachers:
                    sub = feats[(feats["set"] == set_name) & (feats.model_style == s) & (feats.teacher == t)]
                    if sub.empty:
                        continue
                    k = args.top_k if s == o else min(10, args.top_k)
                    cols = ["rank", "feature", "kind", "collision", "coef", "df_model_style", *[f"rate_{v}_own" for v in styles], f"rate_{s}_others"]
                    L += [f"### {set_name} · {s} 模型 · {t}", ""] + _md_table(sub.head(k), cols) + [""]
    L += ["## 运行", "", f"- 命令：`{' '.join(sys.argv)}`", f"- 总耗时 {info['total_runtime_s']:.0f} s；" + "；".join(f"{s}: {set_info[s]['n_texts']} 文本、{set_info[s]['n_families']} family、nnz {set_info[s]['nnz']:,}、{set_info[s]['runtime_s']:.0f} s" for s in sets),
          f"- backend {set_info[sets[0]]['backend']}（scikit-learn {skl}，numpy {np.__version__}）；hash seed / fold seed {args.seed}；文件 sha256 见 lexical_run_info.json", ""]
    (out / "lexical_summary.md").write_text("\n".join(L), encoding="utf-8")
    log(f"wrote {out}/lexical_summary.md ({time.time() - t_start:.0f}s)")


if __name__ == "__main__":
    main()
