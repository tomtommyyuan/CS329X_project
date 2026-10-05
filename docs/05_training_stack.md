# 训练与评估栈（Phase 1 契约）

> 其余文档：[02 模型与数据](02_models_and_datasets.md)、[03 实验](03_experiments.md)（§2 E1、§3 E2、§8 固定协议）、[04 指标](04_eval_metrics.md)。本文是 DATA / TRAIN / EVAL 三个实现者之间的接口契约；改接口先改这里。代码、注释、docstring 用英文。

## 0. 文件归属与依赖

| 模块 | 文件 | 依赖 |
|---|---|---|
| DATA | `src/vcd/train/data.py`、`scripts/10_build_sft_data.py`、`tests/test_train_data.py` | `vcd.schemas`、`vcd.io`、`vcd.teacher.parse` |
| TRAIN | `src/vcd/train/sft.py`、`scripts/11_train_student.py`、`slurm/train.sbatch`、`slurm/README.md`、`tests/test_sft_smoke.py` | `vcd.train.data`（template、SFT 行读取） |
| EVAL | `src/vcd/student/readout.py`、`scripts/12_eval_student.py`、`src/vcd/analysis/e1_metrics.py`、`scripts/13_e1_analysis.py`、`src/vcd/analysis/e3_metrics.py`、`scripts/15_e3_analysis.py`、`slurm/eval.sbatch`、`tests/test_readout.py`、`tests/test_e1_metrics.py`、`tests/test_e3_metrics.py` | `vcd.train.data`（template）、`vcd.teacher.profile`、`vcd.teacher.parse`、`vcd.stats` |
| 契约 | 本文、`pyproject.toml`（extras `train` / `eval`）、`configs/train.yaml`、两个空 `__init__.py` | |

环境：`.venv` 由 uv 管理，**没有 pip**；安装用 `uv pip install -e ".[train]" --python .venv/bin/python`。已装 torch 2.14.1（CPU）、transformers **5.18.0**、datasets 5.0.1、accelerate 1.15.0。transformers 是 5.x：`Trainer` 参数名用 `eval_strategy`、`processing_class`；`AutoTokenizer` 默认 `use_fast`。HF 缓存里已有 `HuggingFaceTB/SmolLM2-135M`（权重 + tokenizer）和 `Qwen/Qwen3-4B-Base` 的 **tokenizer**（11 MB，无权重）。本机无 GPU：所有组件必须有 CPU 路径，用 tiny 模型跑测试；vLLM 是可选 import，缺了回落到 transformers。

现成数据（只读）：

| 文件 | 内容 | 现状 |
|---|---|---|
| `data/prompts/{train,dev,test}_prompts_v2.jsonl` | `Prompt` 行；train 11,944 = 1,493 family × {T1,T3,T5,T6} × 2 order；dev 1,500 = 150 × {T0,T1,T3,T5,T6} × 2；test 2,400 = 300 × {T1,T3,T5,T6} × 2（T0 待生成）；`system` 全部为 `You are a helpful assistant.` | 完整 |
| `data/teacher_phase1/{teacher}_train_demo.jsonl` | `TeacherResponse`，mode demo，T = 0，两种 order 都有 | 采集中，**别等它**；测试用 `data/teacher_v2/{teacher}_demo.jsonl` + `data/prompts/pilot_prompts_v2.jsonl` |
| `data/teacher_phase1/{teacher}_{dev,test}_profile.jsonl` | mode profile；GPT / DeepSeek 带 `p_letters`、`p_x`，1 pass；Claude 10 sample × 2 pass，`p_x` 为 None | 采集中 |
| `data/rewrites_v9/{teacher}/rewrites.jsonl` | 行：`prompt_id, teacher, version(F/C), rewriter, attempt, text, judged, checks, kept`；每 (prompt_id, version) 最多 3 attempt、最多 1 条 kept；`text` 一律以 `Answer: X\nRationale: ` 开头 | 目前只覆盖 pilot 的 300 条；train 集改写后用同格式放到 `--rewrites-dir` 指定目录 |

## 1. Template 与 SFT 样例格式

### 1.1 Template（`src/vcd/train/data.py` 拥有；EVAL 只 import，不复制字串）

```python
ASSISTANT_PREFIX = "Answer:"          # no trailing space, see §1.3

def render_prompt(system: str, user: str) -> str:
    """system line, blank line, user text, blank line, assistant prefix. Used verbatim in training and readout."""
    return f"{system}\n\n{user}\n\n{ASSISTANT_PREFIX}"

def render_target(letter: str, rationale: str) -> str:
    """Canonical assistant completion AFTER the prefix: ' A\\nRationale: ...' (leading space, no trailing whitespace)."""
    return f" {letter}\nRationale: {rationale.strip()}"

def canonical_target(raw: str) -> str | None:
    """Teacher demo / rewrite text -> render_target(letter, rationale). None if no letter or no 'Rationale:' line."""
```

`canonical_target` 用 `vcd.teacher.parse.parse_answer` 取字母；rationale = 第一个 `Rationale:`（大小写不敏感）之后到文末的文本 `.strip()`；去掉 teacher 原文里 `Answer: B  \n` 的两个尾随空格这类噪声。O / F / C 都经过它，三版本只有 rationale 文本不同。

### 1.2 SFT 文件：`data/sft/{teacher}_{version}_s{seed}.jsonl`，一行一个训练样例

| 字段 | 类型 | 说明 |
|---|---|---|
| `prompt_id` | str | 与 prompts 文件一致 |
| `family_id`, `variant`, `order` | str, str, int | 直接复制自 `Prompt` |
| `teacher` | str | `gpt4o` / `claude46` / `deepseek_v4`；R 版本写 `random` |
| `version` | `"O"|"F"|"C"|"R"` | |
| `text_prompt` | str | `render_prompt(system, user)`，**以 `Answer:` 结尾** |
| `text_target` | str | `render_target(...)`，**以空格 + 字母开头**，无尾随空白，不含 EOS |
| `letter` | str | 目标字母，方便检查 R 的均衡与 O 的 choice |
| `n_target_tokens` | int, 可选 | 训练器填（含 EOS），DATA 不填 |

边界：`text_prompt + text_target` 即完整训练文本；`Answer:` 属于 prompt，` A` 属于 target，所以 **target 的第一个 token 就是 readout 读的字母 token**。训练器分别 tokenize 两段再拼接 id（§3.1），readout 对 `text_prompt` 取下一 token 分布（§5），两者的 token 边界由此强制一致。

同一行的 worked example（`dd_9120.T5.o1`，gpt4o 原文 `"Answer: B  \nRationale: It is safer to cancel..."`）：

```json
{"prompt_id": "dd_9120.T5.o1", "family_id": "dd_9120", "variant": "T5", "order": 1, "teacher": "gpt4o", "version": "O",
 "text_prompt": "You are a helpful assistant.\n\nYou're ... \n\nOptions:\nA. ...\nB. ...\n\nShould you ...?\n\nAnswer with the letter of your choice, then give a brief rationale (1 to 3 sentences). Use exactly this format:\nAnswer: <A or B>\nRationale: <your rationale>\n\nAnswer:",
 "text_target": " B\nRationale: It is safer to cancel the vet appointment and reschedule rather than risk the journey without properly securing your pet, as this could endanger both your pet and yourself in the event of an accident or sudden stop.",
 "letter": "B"}
```

### 1.3 为什么 `Answer:` 后不留空格（2026-10-04 用两个 tokenizer 实测）

| | SmolLM2-135M (GPT2Tokenizer) | Qwen3-4B-Base (Qwen2Tokenizer, 151,669 tokens) |
|---|---|---|
| `"Answer:"` | `[Answer][:]` | `[Answer][:]` |
| `" A"` / `"A"` / `" B"` / `"B"` | 单 token：330 / 49 / 389 / 50 | 单 token：362 / 32 / 425 / 33 |
| `tok(prompt + " B\nRationale...") == tok(prompt) + tok(" B\nRationale...")` | **True** | **True** |
| prompt 以 `"Answer: "` 结尾、target 以 `"B"` 开头 | **False**：分开 tokenize 得 `[Ġ][B]`，合并得 `[ĠB]` | **False**，同样 |
| 自动加 BOS | 否 | 否（`bos_token` 为 None；`eos`=`pad`=`<|endoftext|>` 151643） |

结论：prefix 以 `Answer:` 结尾、target 以 ` X` 开头是唯一 train / readout 边界一致的切法；teacher 原文 `Answer: B` 的首 token 本来就是 `ĠB`，和 teacher logprobs 读法同构。全程 `add_special_tokens=False`，不加 BOS；训练时在 target 末尾追加 1 个 EOS（Qwen3 用 `<|endoftext|>`，SmolLM2 用 `<|endoftext|>` id 0）。

## 2. 训练文件的构造（`scripts/10_build_sft_data.py`）

```
10_build_sft_data.py --teacher gpt4o --versions O[,F,C] --seeds 1,2,3,4,5 [--config configs/train.yaml]
                     [--prompts PATH] [--demos PATH] [--rewrites-dir DIR] [--out-dir data/sft]
                     [--order-policy stable_one|both] [--order-seed 20261002] [--no-paired]
                     [--random-label --ref-teacher gpt4o --seeds 1,2,3]
                     [--list-prompt-ids]        # 只写 data/sft/{teacher}_O_prompt_ids.txt，给改写预算用
```

过滤与排序，按顺序执行：

| 步 | 规则 | 计数写入 meta |
|---|---|---|
| 1 过滤 variant | 只用 `data.variants`（T1,T3,T5,T6）；pilot 文件里的 T0 / VC 丢掉 | `n_prompts_in` |
| 2 过滤类别 | demo `category == "answer"`，且 `canonical_target(raw)` 非 None | `n_dropped_category`, `n_dropped_format` |
| 3 order policy | `stable_one`（默认，docs/02 §4.2）：(family, variant) 两个 order 都 answer 且 `choice_action` 相同才保留，然后**只留一个 order**；`both`：两个 order 都留。被留的 order 由 `--order-seed`（固定 20261002，**与 run seed 无关**）决定：`rng = np.random.default_rng([order_seed, zlib.crc32(f"{family_id}.{variant}".encode())])`，`order = 1 + int(rng.integers(2))`。这样 5 个 seed 共用同一批 prompt_id，F / C 只需改写这一半 | `n_dropped_order_unstable`, `order_stable_rate` |
| 4 F / C 可用性 | 版本 F / C 只取 `kept == true` 的最后一条 attempt；`text` 经 `canonical_target`，且其字母必须等于 O 的字母（不等则丢并计数） | `n_dropped_no_rewrite`, `n_dropped_choice_mismatch` |
| 5 paired（默认开） | 本次 `--versions` 里所有版本取 prompt_id **交集**，一个 teacher 的 O / F / C 文件行数相同、prompt_id 集相同；`--no-paired` 关闭。只建 O 时交集就是 O 自己 | `paired`, `n_examples` |
| 6 family 顺序 | `families = sorted(set(family_id))`；`perm = np.random.default_rng(seed).permutation(len(families))`；每个 seed 一次置换，**与 teacher、版本无关**（被过滤掉的 family 直接跳过，相对顺序不变）；family 内按 variant 顺序 T1, T3, T5, T6，再 order 1, 2 | `seed`, `n_families` |

输出：`data/sft/{teacher}_{version}_s{seed}.jsonl` 与 sidecar `data/sft/{teacher}_{version}_s{seed}.meta.json`（上表计数 + `sha256` + `prompts_path` + `demos_path` + `rewrites_dir` + `built_at`）。O 的内容在 5 个 seed 间只差行序。

随机标签控制 R（`--random-label`）：prompt_id 集 = `--ref-teacher` 在同一 seed 下 O 文件的 prompt_id 集（保证 n_examples 相同），family 顺序同上。字母：每个 family 的 k 条样例里 ⌊k/2⌋ 个 A、⌊k/2⌋ 个 B，k 为奇数时多出的那个由 `np.random.default_rng([seed, crc32(family_id)])` 定，再用同一 rng 打乱分配到该 family 的 prompt 上。rationale 固定为 `RANDOM_RATIONALE = "This option is the more reasonable choice in this situation."`（不提情境任何内容）。`teacher = "random"`，`version = "R"`，文件 `data/sft/random_R_s{seed}.jsonl`，默认 seeds 1,2,3。

DATA 还提供给 TRAIN 的读接口：`load_sft_rows(path) -> list[dict]`（校验上表字段存在、`text_prompt.endswith(ASSISTANT_PREFIX)`、`text_target[0] == " "`）。

## 3. 训练（`src/vcd/train/sft.py`、`scripts/11_train_student.py`）

```
11_train_student.py --data data/sft/gpt4o_O_s1.jsonl --run-dir runs/qwen3-4b/gpt4o_O_s1 --seed 1
                    [--config configs/train.yaml] [--profile tiny] [--max-steps N] [--overwrite]
```

没有 `--resume`：只存最终 checkpoint，中断的 run 整个重跑；已有 `train_manifest.json` 的目录默认跳过，`--overwrite` 才重训。

```
```

### 3.1 Tokenize 与 loss

| 项 | 规则 |
|---|---|
| ids | `ids = tok(text_prompt, add_special_tokens=False) + tok(text_target, add_special_tokens=False) + [eos_id]` |
| labels | prompt 段全部 `-100`；target 段与 EOS 为自身 id；pad 为 `-100` |
| pad | `pad_token = eos_token`（两个 tokenizer 都如此）；右 pad，按 batch 动态 pad |
| 超长 | `len(ids) > max_seq_len` 的样例**整条丢弃并计数**（manifest `n_dropped_too_long`），不截断 target；预期 0 条（prompt ≈ 100 token，target ≈ 60 token） |
| 顺序 | **不 shuffle**：文件顺序即训练顺序，每个 epoch 相同（文件已是 seed 置换；sampler 必须是 sequential，不用 `group_by_length`） |
| 梯度累积 | 每个 micro-batch 的 loss 除以**该 step 实际的 micro-batch 数**（epoch 末的不满组按其大小），不是固定除以 accum；manifest `accumulation_group_sizes` 记录出现过的组大小 |
| 随机性 | `torch.manual_seed(seed)`、`numpy`、`random` 同 seed；dropout 为 0（Qwen3 默认） |
| token 数 | `n_target_tokens` = 所有样例 target + EOS 的 token 总数（1 epoch）；`n_total_tokens` 含 prompt；都进 manifest |

### 3.2 超参（`configs/train.yaml`，所有条件共用，只换 `--data` / `--seed` / `--run-dir`）

| 键 | 值 | 备注 |
|---|---|---|
| `student_model` | `Qwen/Qwen3-4B-Base` | `student_model_short: qwen3-4b` 作 runs 路径首段 |
| precision | bf16 | tiny 用 fp32 |
| learning_rate / scheduler / warmup | 1e-5 / cosine / 3% | 全参 |
| epochs | 3 | |
| effective batch | 32 序列 = `per_device 4 × grad_accum 8`（`configs/train.yaml` 与此一致） | 单卡 H100；≈ 5,620 样例 → 176 step/epoch，528 step |
| max_seq_len | 1024 | |
| gradient_checkpointing | true | |
| optimizer | `adamw_torch`，CUDA 上用 **fused** kernel（原地更新，无参数大小的临时张量）；备选 `adamw_8bit`（bitsandbytes，Linux + CUDA，不在 `train` extra 里，需单独 `uv pip install bitsandbytes`） | 显存算术（4.02B 参数）：fp32 权重 15 GiB + fp32 梯度 15 GiB + Adam m,v 30 GiB = **60 GiB 常驻**，再加 autocast 的 bf16 权重缓存 7.5 GiB、logits 与激活；默认 foreach AdamW 在 step 时还要 15 GiB 临时，所以必须 fused。gate run 的 manifest `peak_memory_gib` > 70 就切 8bit |
| weight_decay / max_grad_norm | 0.0 / 1.0 | |
| save | 只存最终 checkpoint，训练中不 eval；**bf16 训练的 checkpoint 存 bf16**（≈ 8 GB/run；manifest `checkpoint_dtype`），tiny / fp32 存 fp32 | vLLM 与 readout 本来就按 bf16 加载；dev、test 两个 readout 都有了就删 `checkpoint/` |
| tiny profile | `HuggingFaceTB/SmolLM2-135M`、8 样例、`max_steps 2`、fp32、`per_device 4 × accum 1`、`max_seq_len 256`、eager attention、不开 checkpointing | `--profile tiny` 把 `tiny:` 下的键覆盖到顶层 |

实现用 HF `Trainer` 或 ≤ 150 行的手写循环都可，但 shuffle 关闭、loss mask、EOS、manifest 字段必须按本文。

### 3.3 输出布局

```
runs/{student_model_short}/{teacher}_{version}_s{seed}/
  checkpoint/                 save_pretrained (safetensors) + tokenizer，vLLM 可直接 LLM(model=该目录)
  train_manifest.json
  train_log.jsonl             每 logging_steps 一行 {step, loss, lr, epoch}
  eval/
    {split}_responses.jsonl   TeacherResponse 行（§5），split ∈ {dev, test}
    {split}_readout_summary.json
```

run id = `"{student_model_short}.{teacher}_{version}_s{seed}"`，例 `qwen3-4b.gpt4o_O_s1`、`qwen3-4b.random_R_s2`、未训练基座 `qwen3-4b.base_B_s0`；正则（唯一定义在 `vcd.train.data.RUN_ID_RE`，trainer / 12 / 13 都 import 它）`^(?P<student>[^.]+)\.(?P<teacher>[a-z][a-z0-9_]*)_(?P<version>[OFCRB])_s(?P<seed>\d+)$`。teacher 段必须以字母开头，所以 `_smoke_gpt4o_O_s1` 这类试跑目录不算协议 run，13 会打警告并跳过；试跑统一放 `runs/_smoke/`。它是 responses 行的 `teacher` 字段。

`train_manifest.json` 必含：`run_id, student_model, student_model_short, teacher, version, seed, data_path, data_sha256, n_examples, n_dropped_too_long, n_target_tokens, n_total_tokens, epochs, steps, effective_batch, learning_rate, lr_scheduler, warmup_ratio, max_seq_len, precision, checkpoint_dtype, peak_memory_gib, optimizer, optimizer_fused, gradient_checkpointing, accumulation_group_sizes, wall_time_sec, git_commit`（`git rev-parse HEAD`，失败则 null）, `torch_version, transformers_version, hostname, started_at, finished_at, final_loss`。

## 4. 评估入口（`scripts/12_eval_student.py`）

```
12_eval_student.py --run-dir runs/qwen3-4b/gpt4o_O_s1 --split dev|test|pilot|train [--prompts PATH] [--sft PATH]
                   [--backend auto|vllm|transformers] [--batch-size 32] [--limit N] [--config configs/train.yaml] [--profile tiny]
                   [--model PATH]      # 不经 run-dir，直接评一个模型（S_0 基线：Qwen3-4B-Base 不训练）
```

读 `--prompts`（默认按 split 取 `paths.prompts_{split}`），**所有 variant、两个 order 都评**（dev 含 T0），写 `eval/{split}_responses.jsonl` 与 `eval/{split}_readout_summary.json`（n、各 category 占比、`mean_mass_AB`、top1 token 直方图前 10、backend、耗时、dtype、batch_size）。`--model` 模式的 run id 用 `"{student_model_short}.base_B_s0"`。

`--split train`（2026-10-05 加，E1a / E1b 用）：只评该 run **自己的训练 prompt**，prompt_id 取自 SFT 文件（manifest 的 `data_path`，或 `--sft PATH`；`--model` 模式必须给 `--sft`），从 `paths.prompts_train` 取 Prompt，按文件顺序，只评训练过的那个 order（`vcd.student.readout.sft_prompts`）；输出 `eval/train_responses.jsonl`、`eval/train_readout_summary.json`（多记 `sft_path`、`sft_sha256`）。其它行为不变。

## 5. Readout 规范（`src/vcd/student/readout.py`）

```python
LETTERS = ("A", "B")

def letter_token_ids(tokenizer) -> dict[str, list[int]]:
    """{'A': [id(' A'), id('A')], 'B': [id(' B'), id('B')]}; asserts each spelling is exactly one token."""

def readout_rows(prompts: list[Prompt], next_token_probs: np.ndarray, token_ids: dict, tokenizer, run_id: str,
                 model_name: str, backend: str, answer_mass_min: float = 0.9) -> list[TeacherResponse]:
    """Pure function from the unrestricted next-token distribution (n_prompts x vocab, or top-k dict per prompt) to rows."""

class TransformersBackend:  # forward pass, full softmax; CPU ok
class VllmBackend:          # optional import; SamplingParams(max_tokens=1, temperature=0, logprobs=top_logprobs), raw string prompts

def run_readout(model_path, prompts, run_id, backend="auto", batch_size=32, dtype="bfloat16", top_logprobs=20) -> list[TeacherResponse]
# 2026-10-05 决定：实际评估用 configs/train.yaml 的 readout.backend = transformers、readout.dtype = float32（gate 测出 bf16 读数噪声 mean 0.007 / max 0.06，vLLM top-20 截断又加一层）；训练仍为 bf16
```

| 项 | 规则 |
|---|---|
| 输入串 | `render_prompt(p.system, p.user)`，与训练 `text_prompt` 逐字节相同；`add_special_tokens=False`，不加 BOS，不用 chat template |
| 读什么 | 下一 token 的**无限制** softmax 分布 `q`（vLLM：top-k logprobs 的 exp，缺失 token 记 0；transformers：全词表） |
| 字母质量 | `m_A = q[id(" A")] + q[id("A")]`，`m_B` 同理；只用这两种拼法（`(A`、`**A` 等不算，它们在训练目标里不存在） |
| `p_letters` | `{"A": m_A/(m_A+m_B), "B": m_B/(m_A+m_B)}`；`m_A + m_B == 0` 时 `p_letters = None`、category `malformed` |
| `letter` | argmax of `p_letters` |
| `choice_action` | `p.letter_to_action[letter]` |
| `p_x` | `vcd.teacher.parse.p_x_from_letters(p_letters, p.letter_to_action)` |
| `category` | `"answer"` iff `m_A + m_B >= answer_mass_min`（0.9），否则 `"malformed"`；学生 readout 不产生 refusal / insufficient |
| `usage` | `{"top1": tokenizer.decode([argmax q]), "top1_id": int, "top1_p": float, "mass_AB": m_A + m_B, "backend": "vllm"|"transformers", "n_prompt_tokens": int}` |
| 其它字段 | `teacher = run_id`，`model = checkpoint 路径或 HF 名`，`mode = "profile"`，`temperature = 0.0`，`pass_idx = 0`，`sample_idx = 0`，`raw = "Answer:" + usage["top1"]`，`cached = False`，`timestamp` ISO |
| 两个 order 平均 | 不在 readout 做；`profile.symmetrize` 负责（每行一个 order） |

vLLM：`LLM(model=ckpt, dtype="bfloat16", max_model_len=1024, gpu_memory_utilization=0.85, seed=0, max_logprobs=max(top_logprobs, 20))`（引擎默认上限 20，不抬高则 `readout.top_logprobs` 调大会被拒）；prompt 在本地 `add_special_tokens=False` tokenize 后以 `prompt_token_ids` 送入；`SamplingParams(max_tokens=1, temperature=0.0, logprobs=top_logprobs)`；取 `out.outputs[0].logprobs[0]`（`token_id -> Logprob`），字母 token 不在 top-k 时质量记 0（上界 = 第 k 名的概率；训练过的学生字母是 top-1，未训练基座的 `mass_AB` 相对 transformers 会偏低，gate run 在 dev 上比对两后端）。transformers：`model(input_ids, attention_mask)` 取最后一个非 pad 位置的 logits（右 pad 要用 `attention_mask.sum(1) - 1` 索引），`softmax` 后按上表。两后端在 tiny 模型上 `p_letters` 差 < 1e-3 由 `tests/test_readout.py` 检查（vLLM 缺席时跳过）。

E0.7 校验（HAIC 上做一次，Qwen3-4B-Base 原模型 + dev 前 1,000 条 prompt）：同一 prompt 的 first-token `p_letters["A"]` 与 k = 10、T = 1 采样的字母频率，`mean_abs_diff > 0.05` 则学生评估也改用采样（复用 `vcd.readout.logit_vs_sample.summarize`）。

## 6. E1 / E2 指标（`src/vcd/analysis/e1_metrics.py`、`scripts/13_e1_analysis.py`）

全部从 `TeacherResponse` 行出发，先经既有管线：`responses_to_frame → align_to_focus(focus_by_family) → cell_estimates → symmetrize → framing_shifts(variants)`。学生行 `mode == "profile"`，`cell_estimates` 直接用 `p_x`；teacher 行同样处理（Claude 用采样频率）。所有 `sym` 表的 `teacher` 列可以是 run id 或 teacher 名，函数不区分。记号见 docs/04 §0。

```python
RunKey = NamedTuple("RunKey", student=str, teacher=str, version=str, seed=int)
def parse_run_id(run_id: str) -> RunKey
def binary_jsd(p: np.ndarray, q: np.ndarray) -> np.ndarray          # base-2, 与 profile._jsd 相同；对称化 p 指 p_sym
def load_run_responses(runs_dir: Path, split: str, student_short: str | None = None) -> list[TeacherResponse]   # 读全部 runs/*/*/eval/{split}_responses.jsonl
def sym_table(responses, prompts: dict[str, Prompt], focus_by_family: dict[str, str], mass_gate=True) -> pd.DataFrame   # 封装上面四步；mass_gate=False 把带 p_x 的 malformed 行也当 answer，只给 base_prior_shifts 用
def base_prior_shifts(rows, prompts, variants) -> pd.DataFrame       # 基座先验 profile r_0：sym_table(mass_gate=False) → framing_shifts；协变量，不是 S_0 的 readout
def category_rates(frame: pd.DataFrame, by=("teacher", "variant")) -> pd.DataFrame      # answer / malformed 占比；profile.answer_rates 只看 demo 行所以另写
def order_gap(sym: pd.DataFrame) -> pd.DataFrame                    # per teacher: mean |p_o1 - p_o2|, share (p_o1>0.5)==(p_o2>0.5)  (docs/04 组 A)
def teacher_agreement(sym_s: pd.DataFrame, sym_t: pd.DataFrame, variants, by_variant=False) -> pd.DataFrame
    # 行 = (run_id, teacher)；agreement = mean_{(i,j)} [ (p_s>0.5) == (p_t>0.5) ]，只用两边都有 p_sym 的 cell；
    # 任一边恰好 p_sym == 0.5 的 cell 不进分母（majority 未定义），数量记在 n_ties；by_variant 加 variant 列  (组 C)
def student_teacher_jsd(sym_s, sym_t, variants, by_variant=False) -> pd.DataFrame        # mean_{(i,j)} binary_jsd(p_s, p_t)  (组 C)
def consistency(sym: pd.DataFrame, variants) -> pd.DataFrame        # = profile.teacher_consistency + pairwise_flip_rates 合表：flip_rate, mean_jsd, family_flip_share, share_uncertain  (组 B)
def seen_vs_unseen(sym, seen=("T1","T3","T5","T6"), unseen="T0") -> pd.DataFrame        # flip / JSD 在 seen 内部 vs (unseen, T1)；test 无 T0 时返回空表
def inheritance(shifts_s: pd.DataFrame, shifts_t: pd.DataFrame, own: dict[str, str], n_perm=10_000, n_boot=10_000, seed=0, by_variant=False, control=None) -> pd.DataFrame
    # 每个 run：rho_own, rho_other (每个 other teacher 一列或长表), rho_other_max, other_argmax, delta_rho = rho_own - rho_other_max,
    # rho 用 Pearson（另给 spearman 列），对齐在 (family, variant) 交集上；r 已是 family 内去均值（framing_shifts 保证）
    # p_perm：打乱该 run 的 family 标签（整 family 置换，variant 结构保留）n_perm 次重算 delta_rho，p = (count(perm >= observed) + 1) / (n_perm + 1)（下限 1 / (n_perm + 1)）；
    #   perm_null_mean / perm_null_sd 描述这个 null——它不以 0 为中心（置换保留各 profile 的 variant 主效应），所以 p_perm 旁边一定印 null 均值
    # ci：family bootstrap n_boot 次的 2.5 / 97.5 分位
    # control=<一张只含 r_0 的 shifts 表>：所有 rho 换成给定 r_0 的 partial Pearson（两边先对 [1, r_0] 回归取残差），family 还要对 control 完整，
    #   多出 control（名字）、rho_base（学生与 r_0 的 raw Pearson）两列；置换只打乱学生的 family，teacher 与 r_0 不动；bootstrap 三方联动重抽
def inheritance_partial(shifts_s, shifts_t, control, own, variants, n_perm, n_boot, seed, by_variant=False) -> pd.DataFrame   # = inheritance(control=...)；ΔρPartial 的命名入口
def partial_corr(x, y, z) -> float                                                         # 标量版 partial Pearson r(x, y | z)
def profile_rho_partial(shifts_s, shifts_t, control, variants, by_variant=False) -> pd.DataFrame   # 每 (run, teacher)：partial, raw, rho_base, n_cells
def pooled_shifts(shifts_s, runs: list[str], name: str) -> pd.DataFrame                 # 同 (student, teacher, version) 的各 seed 的 r 取平均 -> 一张 shifts 表
def pooled_inheritance(shifts_s, shifts_t, own, variants, n_perm, n_boot, seed, control=None) -> pd.DataFrame
    # 每个 (teacher, version) 一行：seed-mean profile 的 rho_own / delta_rho / p_perm / CI，加 Holm 校正的 p_holm（同一 version 内跨 teacher）
def pooled_inheritance_partial(shifts_s, shifts_t, control, own, variants, n_perm, n_boot, seed) -> pd.DataFrame   # P3：= pooled_inheritance(control=...)
def holm(pvals) -> np.ndarray                                                             # Holm step-down 校正 p
def n_label_assignments(labels) -> int; def label_assignments(labels) -> np.ndarray     # 多重集 labels 的全部不同排列（15 run / 3 × 5 → 756,756 行，numpy 枚举 < 0.1 s）
def grid_permutation(table: pd.DataFrame, n_perm=10_000, seed=0, exact_max=0) -> dict   # 打乱 run → teacher 归属（每 teacher 5 个不变），mean delta_rho 的 null 与 p；exact_max=0 随机 n_perm 次（原规则）
def grid_permutation_partial(table, n_perm=10_000, seed=0, exact_max=1_000_000) -> dict  # P1：输入 inheritance_partial 表，归属数 ≤ exact_max 时枚举全部（method "exact"，p 下限 1/756,756），否则随机
def suggestibility_by_run(shifts, pos="T5", neg="T6", families=None) -> pd.DataFrame    # 每个 profile 的 s = δ(T5) − δ(T6)：who, delta_T5, delta_T6, s, n_families；families 限定 family 集（P2 传公共集）
def dose_response(s_runs: dict, s_teachers: dict, own: dict, n_perm=10_000, seed=0, exact_max=1_000_000) -> dict
    # P2：15 个 O run 的 s 对自己 teacher 的 s_T 做 OLS，slope / intercept / pearson；p 单侧（slope > 0），null = 同上的 run → teacher 重指派（枚举或随机）；
    # s_run 与 s_T 由 13 在同一 family 集上算：对每个 O run、每个 teacher 和 r_0 都完整的 family（`complete_families`；dev 139 个），不是各自的完整集
    # p 约定：exact = 全部不同指派中（含观测指派）统计量 ≥ 观测的占比（下限 1/756,756）；random = (count + 1) / (n + 1)
    # 另给每 teacher 的学生 s 均值 / sd、pooled 组内 sd（seed_noise_sd）、学生均值排序是否等于 teacher 排序（ordering_preserved）
# 2026-10-05 更正（family 作推断单位；P1 / P2 的 run-level p 伪复制，只作描述）
def e2_primary_verdict(n_pass, n_teachers) -> str                                       # "PASS"（≥ 2/3）/ "PARTIAL"（≥ 1）/ "FAIL"（0）
def teacher_assignments(k) -> np.ndarray                                                  # k! 种 teacher 重标号（恒等在首行）
def teacher_level_exact_p(table) -> dict                                                  # inheritance(_partial) 表的 mean Δρ 对 k! 重标号的精确 p（observed, p, rank, n_assignments, floor=1/k!, null）；dose_response / grid_permutation_partial 的结果里也各带一个 teacher_exact
def joint_partial_D(shifts_students_pooled_by_teacher: dict[str, DataFrame], shifts_teachers, control, variants, cells=None, n_perm, n_boot, seed) -> dict
    # 次级统计量 D：M[k, j] = partial ρ(r_{S_k}, r_{T_j} | r_0)（control=None 则 raw），S_k = teacher k 的 seed-mean 学生（pooled_shifts）；D = mean_k [M[k,k] − mean_{j≠k} M[k,j]]
    # cells 限定进相关的 variant 子集（T0-only：variants = T0 + seen，cells = ["T0"]）；family 对所有学生、teacher、r_0 完整
    # ci：family bootstrap（三方联动）；p_perm：对学生的**残差**（给定 r_0）做同一个 family 置换，teacher 与 r_0 不动，(count + 1) / (n + 1)（偏相关用的就是残差；dev 上置换原始 profile 的 null 不可区分，sd 0.020 vs 0.022）
    # 分解 D = D_shared + D_specific（E_k = Ē + U_k；D_shared = 共享学生残差 × 行尺度 ‖E_k‖ 不等，不含 own-teacher 信息，行尺度相等时精确抵消）；D_specific 自带 ci_specific_lo / hi 与 p_perm_specific；
    #   D_scalefree = 每行除以 pooled 尺度 s̄（shared 部分精确抵消）+ ci_scalefree_*，探索
    # 返回 D, D_raw, D_shared, D_specific, D_scalefree, ci_*, p_perm(_specific), null_mean(_specific), null_sd(_specific), row_scale, matrix, matrix_raw, matrix_shared, matrix_specific,
    #   per_teacher（每行 contrast 与 contrast_specific）, n_families, cells, control
def e2_secondary_verdict(d: dict, alpha=0.05) -> str                                   # "pass" 当 D > 0、ci_lo > 0、p_perm < alpha 且 ci_specific_lo > 0；缺 D 或缺重抽样 → "pending (...)"；否则 "fail"
def reliability_ceiling(split_half_r: float) -> float                                    # sqrt(2r / (1 + r))：symmetrized profile 的 Spearman-Brown 可靠度开方 = 任何变量与它的相关上限（test Claude 0.329 → 0.704，DeepSeek 0.466 → 0.797，GPT-4o 0.691 → 0.904）；r ≤ 0 → nan
def suggestibility_groups(shifts, groups: dict[str, list[str]], families, pos, neg, n_boot, seed) -> (DataFrame, DataFrame)
    # 每组（某 teacher 的 5 个 O run、某 teacher 自己、R run、base prior）的 s = δ(T5) − δ(T6) 与 family-bootstrap CI；第二张表是全部两两差及 CI（同一重抽样，配对）
def base_prior_control(shifts_0, shifts_t, variants, n_boot, seed) -> DataFrame
    # e2_plan 的 S_0 控制行，用 ungated covariate profile r_0：对每个 teacher 的 raw ρ 与 CI、rank、margin = ρ − max ρ(other) 与 CI；最近 teacher 的 margin CI 含 0 → 控制成立
def letters_of(rows) -> dict[str, str | None]                                            # prompt_id → argmax letter
def train_reproduction(letters: dict, targets: dict) -> dict                             # E1a：n_targets, n_scored, n_missing, n_no_letter, n_match, accuracy
def contested_items(own_targets, other_targets) -> list[str]                            # 两 teacher 标签不同的训练 prompt_id（同一 prompt_id，故同一 order）
def contested_alignment(letters_by_run, own_targets, other_targets, n_boot=10_000, seed=0, family_of=None) -> dict
    # E1b：seed 合并后，争议项上学生给自己 teacher 字母的 (item, run) 对占比 share，family bootstrap 95% CI（ci_lo, ci_hi），n_items, n_families, n_runs, n_pairs
def seed_noise_null(metric_table: pd.DataFrame, value: str) -> pd.DataFrame
    # 输入列 run_id, teacher, version, seed, <value>；输出每 (teacher, version) 的 seed 两两 |差| 的 n_pairs, mean, sd, q95，以及 pooled 一行 (teacher="all")
def effect_in_null_sd(diff: float, null_row: pd.Series) -> float   # 效应量 = diff / null sd
def shared_component_r2(shifts_s, shifts_t, own: str, others: list[str]) -> float      # r_s 对 [r_own, r_other...] 的 OLS R²  (组 D)
```

`13_e1_analysis.py --runs-dir runs --student qwen3-4b --split test [--teacher-dir data/teacher_phase1 | --teacher-files gpt4o=path,...] [--prompts ...] [--prompts-train ...] [--sft-dir data/sft] [--exact-max 1000000] [--out results/e1]` 输出：

| 文件 | 内容 |
|---|---|
| `category_rates.csv`、`order_gap.csv`、`agreement.csv`（+ `_by_variant`）、`jsd.csv`、`consistency.csv`、`seen_vs_unseen.csv`、`e1_table.csv`、`seed_null.csv` | 描述性 E1（agreement / JSD / 一致性）；JSD 标注为受 teacher 校准混淆 |
| `e1_train_reproduction.csv`、`e1_contested.csv` | E1a / E1b；需要 `eval/train_responses.jsonl` 与 SFT 文件（`--sft-dir`；O 文件缺失时从 `{teacher}_train_demo.jsonl` 用 `select_demo_targets` 重建） |
| `inheritance_pooled.csv` | **E2 primary**：每 teacher seed-mean 的 uncontrolled Δρ、family permutation p 与 `perm_null_mean` / `perm_null_sd`、Holm p、`passed` |
| `e2_secondary_D.json` | **E2 secondary**：`seen_partial`（判定用）、`T0_partial`、`seen_raw`（探索）各含 D、D_shared / D_specific / D_scalefree、CI、p、四张矩阵、`row_scale`；`verdict`、`rule`、`reliability_split_half_r`、`ceiling_sqrt_spearman_brown` |
| `inheritance.csv`、`inheritance_by_variant.csv`、`grid_permutation.json` | 每 run / 按 variant 的 uncontrolled Δρ；原预注册的随机归属 grid permutation（描述） |
| `inheritance_partial.csv`、`inheritance_partial_by_variant.csv`（含 T0 行）、`inheritance_partial_pooled.csv`、`grid_permutation_partial.json` | 描述：ΔρPartial 每 run、按 variant、seed-mean（P3）；run-level 归属枚举（P1 数字）+ `teacher_exact` |
| `suggestibility_runs.csv`、`suggestibility_groups.csv`、`suggestibility_group_pairs.csv`、`dose_response.json` | 描述：每 profile / 每组的 s 与 CI、两两差；剂量反应 slope（P2 数字）+ `teacher_exact` |
| `base_control.csv` | S_0 控制行（ungated covariate profile 对每个 teacher 的 ρ、margin 与 CI） |
| `summary.md` | Verdicts、Reliability ceilings 段、Descriptive 表、全部表、"Pre-revision rule versions" 披露节；区分"没有 run"、"有 run 但全部 malformed"、"pending" |

**决策规则（2026-10-05 在 dev 上冻结并于同日更正，test 只评一次）**：

| 判定 | 规则 | pending 条件 |
|---|---|---|
| E1a | 每个 O run 在自己的训练 prompt 上 argmax 字母 = SFT 目标字母的比例 ≥ 0.95，且 `n_missing == 0`；`answer_rate` 同表报，不进门 | 任一 teacher 的 O run 无 `train_responses.jsonl` 或无 SFT 目标 → E1a、E1b、E1 三行都 `pending` |
| E1b | 对每个 other teacher：争议训练项上 5 seed 合并后学生给 own 字母的比例，family-bootstrap 95% CI 下界 > 0.5 | 同上 |
| **E1** | 三个 teacher 的 E1a 与 E1b 都过 | 任一 pending → `pending (...)` |
| **E2 primary** | 原预注册规则：每 teacher seed-mean 的 uncontrolled Δρ = ρ(own) − max ρ(other) > 0 且 family permutation（10,000）Holm p < 0.05；≥ 2/3 teacher → **PASS**，恰 1/3 → **PARTIAL**，0/3 → **FAIL** | 没有 pooled O profile |
| **E2 secondary** | 预先声明：D（见过的 framing、给定 r_0 的偏相关）> 0、family bootstrap 95% CI 不含 0 且 family permutation p < 0.05，**且** D_specific（D = D_shared + D_specific）的 family bootstrap CI 下界 > 0 → pass，否则 fail（`e2_secondary_verdict`） | 没有 B run（r_0）或 O run 的 teacher < 2 |
| 描述（无判定） | run-level mean ΔρPartial 与 slope + teacher 层面精确 p（6 种重标号，下限 1/6；run-level 756,756 枚举的 p 伪复制，不是检验）；P3；T0-only D、raw D 与 D_scalefree；各组 suggestibility 与两两差（检验的说法："SFT 用训练标签里的 framing–标签关联替换了基座的 suggestibility"）；S_0 控制行 | — |

每个 ρ_own 旁印上限 `reliability_ceiling(r)` = sqrt(2r / (1 + r))（r = teacher 的顺序 split-half 可靠度，`RELIABILITY`，docs/E0_results §13；`--reliability` 给 r，可覆盖）与 ρ / 上限，每张矩阵 / 每 run 表的 teacher 列下加一行列上限；r 本身不是上界（dev 上 r_0 与 DeepSeek 的 ρ 0.533 > r 0.515）。E0 门槛看 r：test 侧 ≥ 2 个 teacher 的 r < 0.5 时自动印 docs/03 §1 原文（"RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5"，本项目做其中的 E3）。split ≠ test 时 Verdicts 表下自动加一行：该 split 是选规则的 split，判定只是描述性；只有 `results/e1`（test）是确认性的。summary 还印 Conventions（family permutation / bootstrap / teacher 层面精确 p 的约定、公共 family 数）。

规则版本（全部留档，e2_plan §2 有完整披露）：原 E1 = 每个 O seed `agree_own > agree_other_max`（dev gpt4o 2/5、claude46 4/5）；c2c9d96 的 P1 / P2 run-level 置换（同日撤回，伪复制）；不带 D_specific 守门的 secondary D（版本 4，冻结前被版本 5 取代）；summary 的 "Pre-revision rule versions" 节印旧 E1 规则、P1 / P2 的数字与版本 4 的单看 D 读数。

随机标签学生 R 的 agreement / JSD 与 O 学生同表列出，一致性永不单独报；R 与 S_0 不进 P1 / P2 统计，只在表里描述。

## 6b. E3 指标（`src/vcd/analysis/e3_metrics.py`、`scripts/15_e3_analysis.py`；计划 [tasks/e3_plan.md](../tasks/e3_plan.md)）

复用 §6 的管线与函数（`sym_table`、`framing_shifts`、`base_prior_shifts`、`complete_families`、`joint_partial_D`、`suggestibility_groups`、`pooled_shifts`、`holm`、`parse_run_id`）。学生按 teacher 内 **seed 配对**比较（S_{T,V,s} vs S_{T,O,s}），单位 family，噪声参照 = seed-pair null（单对量，按 √n_seeds 缩到 seed 均值，t 参照；e3_plan §3）。组 C 的量（agree_own、jsd_own、drift）是 complete family 上的 family 单位均值，与 §6 E1 表的 cell 加权值略有差异（claude46_O_s1 dev：0.8498 vs 0.8526）；flip / JSD 与 E1 完全一致。全部纯函数。

```python
VERSIONS = ("O", "F", "C"); DISAGREEMENT_PAIRS = (("F","C"), ("O","F"), ("O","C")); CHECKS = ("choice","reasons","conditions","strength","style","format")
def run_grid(run_ids, versions=VERSIONS) -> pd.DataFrame                 # 每 (student, teacher, seed) 一行，每版本一列放 run id（缺则 None）；R / B 忽略
def grid_inventory(grid, versions) -> pd.DataFrame                       # 每 teacher 各版本 seed 数、seed 列表、与 O 配对数（summary 的 Run inventory）
def seed_pairs(grid, version) -> list[(teacher, run_V, run_O, seed)]
def cell_matrices(sym, variants) -> dict[who, DataFrame]                 # 每个 profile 的 family × variant p_sym 表（只留完整 family）
def family_consistency(piv) -> DataFrame[flip, jsd]                      # 每 family：variant 对里多数行动不同的比例、两两 JSD 均值（组 B）
def family_compare(piv_a, piv_b, margin=0.1) -> DataFrame[disagree, agree, jsd, n_ties, disagree_conf, n_conf]   # 每公共 family：多数行动不同的 variant 比例（p = 0.5 的 cell 为 tie 不计）、JSD 均值；_conf = 两边 |p − 0.5| ≥ 0.1 的 cell 上的同一比例
def teacher_families(mats, grid, versions) -> dict[teacher, list[family]]  # 每 teacher 所有 run（全部版本）都完整的 family 集；null 与配对统计量共用
def run_scalars(mats_s, mats_t, families=None) -> DataFrame              # 每 run 一行：flip, jsd, agree_own, jsd_own（seed-pair null 的输入）；families 限定每 teacher 的 family 集
def paired_delta(values: dict[run, Series], grid, versions, n_boot, seed, label, families=None) -> (per_seed, per_teacher)
    # 每 family 量的 V − O 配对差：同 teacher 所有配对 run 的公共 family（∩ families[teacher]）；每 seed 一行；每 teacher seed 均值 + family bootstrap CI（各 seed 联动）+ direction
def cross_student_disagreement(mats, grid, pairs=DISAGREEMENT_PAIRS, n_boot, seed, families=None) -> (per_seed, per_teacher)   # (1) 同 teacher 同 seed 两版本的分歧率、JSD、disagree_conf
def seed_pair_disagreement(mats, grid, version="O", families=None) -> DataFrame   # (1) 的 null：O seed a vs O seed b 的分歧率，每 teacher C(5,2) 对
def excess_disagreement(dis_t, spd, value="disagree") -> DataFrame       # (1) 的判定量：每 (teacher, pair) 的分歧率 − 该 teacher 自己 O-O 均值（oo_mean），var_oo_mean = delete-one-seed jackknife 方差，CI 同样平移
def consistency_delta(mats, grid, versions=("F","C"), n_boot, seed, families=None) -> (per_seed, per_teacher)   # (2) metric ∈ {flip, jsd}
def drift_delta(mats_s, mats_t, grid, versions, n_boot, seed, families=None) -> (per_seed, per_teacher)         # (3) metric ∈ {agree, jsd}（对自己 teacher）
def seed_pair_null(run_table, value, version="O") -> DataFrame           # 每 teacher 的 O seed 两两 value 差（signed + abs），跨 teacher 合并（单对量）
def null_summary(values) -> dict(n, mean, sd, q95)
def e3_verdict(stats: dict[teacher, float], null, one_sided=False, n_seeds=1 | dict, cis=None, extra_var=None, null_groups=None, df=None, n_required=3, min_frac=2/3, alpha=0.05) -> dict
    # 规则 7（e3_plan §3）：SD_stat = sqrt(sd_1² / n_seeds + extra_var)，sd_1 = sqrt(mean(d²))（单侧：null_groups 组内 sd），q95 = t(1 − α/2, df) × SD_stat（单侧 t(1 − α)）
    # |stat| > q95 的 teacher ≥ ceil(2/3 × n_required) 且符号相同 → "effect"；否则 ≥ 同样多的 teacher 过 TOST（CI 与 stat 都在 ± 1 SD_stat 内）→ "no effect"，否则 "inconclusive"
    # 无配对 run → "pending (no paired runs)"；teacher < n_required → "pending (n_teachers k < 3)"；null < 2 → pending
    # 每 teacher：stat, null_sd, q95, effect_sd, exceeds_q95, exceeds_q95_single（单对 95 分位，敏感性）, sign, p_null（t 参照）, p_holm, tost, ci；顶层 q95, q95_single, null_sd_single, n_pass, n_tost, direction
def homogenization(mats, grid, versions=VERSIONS, n_boot, seed) -> (per_cell, per_version)
    # (4) 每版本：不同 teacher 的学生两两（同 seed）判断 JSD 与 1 − corr(r)，同一 family 集（所有 run 都完整）；每版本均值 + CI，与 O 的配对差 d_*_vs_O + CI
    # 校准列：mean_abs_margin、share_low_margin（|p − 0.5| < 0.1）、maj_disagree、maj_disagree_conf（JSD 会随 readout 向 0.5 收缩而机械变小，1 − corr 无尺度，先看它）
def inheritance_by_form(shifts_s, shifts_t, control, grid, variants, versions=("F","C"), n_boot, seed) -> (per_run, per_seed, per_teacher)
    # (5) 每 run 的 Δρ（control = r_0 时为 partial，同 teacher 所有 run + 所有 teacher + r_0 完整的同一 family 集）；V − O 配对差，每 teacher seed 均值 + family bootstrap CI（各 run 联动重抽）
def joint_D_by_version(shifts_s, shifts_t, control, grid, variants, versions, n_perm, n_boot, seed) -> (DataFrame, dict)   # 每版本 seed-pooled 学生的 joint_partial_D（D, CI, p, D_specific, D_shared, D_raw, e2_secondary_rule）
def suggestibility_by_version(shifts_s, shifts_t, grid, versions, families=None, pos="T5", neg="T6", n_boot, seed) -> (groups, diffs)
    # 组 students:{T}:{V} 与 teacher:{T}；diffs = s(students:T:V) − s(students:T:O)、s(students:T:V) − s(teacher:T) 及配对 CI
def load_sft_versions(sft_dir, teacher, seed=1, versions) -> dict[version, rows]; def load_rewrites(path) -> list[dict]
def kept_attempts(rewrites, version) -> dict[prompt_id, row]             # 最后一条 kept attempt（与 vcd.train.data.kept_rewrites 同选法）
def rewrite_yield(rewrites) -> DataFrame[version, n_attempted, n_kept, kept_share, mean_attempts]
def rationale_of(text_target) -> str
def content_check(sft_by_version, rewrites, tokenizer=None, versions) -> DataFrame
    # (6) 每版本：n_items, n_families, same_prompt_set_as_O, letter_identity_with_O（必须 1.0）, letter_matches_rewrite, kept_attempt_found, check_{六项}, mean_attempts, n_attempted / n_kept / kept_share, mean_words, mean_chars, mean_target_tokens, n_target_tokens
def register_features(text) -> dict                                      # contraction_rate, formal_connective_rate, formal_word_rate（闭合词表）, mean_word_len, words_per_sentence, fk_grade（FK 代理）, n_words, n_sentences
def register_table(sft_by_version, versions) -> (per_item, per_version)
def register_separation(per_item, a="F", b="C", features=REGISTER_FEATURES, n_folds=10, seed=0) -> dict
    # LOO 最近质心准确率（标准化与质心都只用 n − 1 条训练项，无泄漏）+ 10 折 ridge logistic（numpy IRLS）准确率，各带 Wilson 95% CI（nc_ci_*, lr_ci_*）、每特征 Cohen d；passes = 两者 ≥ 0.90（e3_plan §2 冻结的门槛）；某版本 < 2 条 → pending
def wilson_ci(k, n) -> (lo, hi)
```

`15_e3_analysis.py --runs-dir runs --student qwen3-4b-paired --split dev|test [--base-run runs/qwen3-4b/base_B_s0] [--teacher-dir data/teacher_phase1] [--teachers ...] [--prompts ...] [--versions O,F,C] [--sft-dir data/sft_paired --sft-seed 1] [--rewrites-dir data/rewrites_train] [--tokenizer Qwen/Qwen3-4B-Base|none] [--out results/e3_{split}] [--n-boot 10000 --n-perm 10000] [--frozen-commit <hash>]` 输出（df = Σ_T (n_O,T − 1)，n_required = 配置里的 teacher 数）：

| 文件 | 内容 |
|---|---|
| `run_inventory.csv`、`run_scalars.csv` | 每 teacher 各版本的 seed 与配对数；每 run 的 flip / jsd / agree_own / jsd_own |
| `seed_pair_null.csv`、`seed_pair_null_summary.csv` | O seed 两两的 flip、jsd、agree_own、jsd_own、delta_rho 差与 O-vs-O 分歧率 / 学生间 JSD；每个量的 n、mean、sd、q95 |
| `disagreement.csv`（+ `_by_seed`）、`disagreement_excess.csv` | (1) 每 teacher × {F-C, O-F, O-C} 的分歧率、disagree_conf 与 JSD 及 CI；对自己 O-O 均值的 excess 与 jackknife 方差（判定量） |
| `consistency_delta.csv`、`drift.csv`（各 + `_by_seed`） | (2) flip / JSD 的 V − O；(3) agree / JSD（对自己 teacher）的 V − O；每 teacher CI 与 direction |
| `homogenization.csv`（+ `homogenization_cells.csv`） | (4) 每版本的 1 − corr 与 JSD 及 CI、与 O 的配对差、|p − 0.5| 校准列 |
| `inheritance_by_form.csv`（+ `_by_seed`、`_runs`） | (5) ΔρPartial 的 V − O 每 teacher CI；每 run 的 ρ_own / ρ_other_max / Δρ / ρ_base |
| `joint_D_by_version.csv` / `.json`、`suggestibility_by_version.csv`、`suggestibility_version_diffs.csv` | 每版本 D（含 D_specific、D_shared、D_raw）；每 (teacher, version) 组的 s 与版本差 |
| `content_check.csv`、`register_check.csv`、`register_separation.csv` | (6) 阶段 2 检查（summary 单独列出 letter_identity_with_O / letter_matches_rewrite / kept_attempt_found < 1 的文件）；register 特征均值；F–C（判 ≥ 0.90，Wilson CI）与 O–F、O–C（描述）的可分性 |
| `verdicts.csv` / `.json` | 13 行规则 7 判定：metric、family、tier（primary 9 / secondary 4）、每 teacher stat [CI] (effect_sd, p, Holm, TOST)、null_q95（统计量尺度）、null_q95_single（单对）、null_sd、n_null、df、n_pass、n_pass_single、n_tost、n_teachers、n_required、direction、p_row、p_row_holm_primary、verdict ∈ {effect, no effect, inconclusive, pending (...)} |
| `summary.md` | 头部 "pre-specified …; not yet frozen / frozen at commit <hash>"、规则原文与操作化、Run inventory、Verdicts（split ≠ test 标 descriptive）、null、(1) 到 (6) 全部表、pending 原因 |

降级：缺 F / C → 对应行 `pending (no paired runs)`；只有部分 teacher 有 F / C → `pending (n_teachers k < 3)`（部分网格不出 effect）；null、O 版本的 homogenization / D / s 照出；缺 base readout → raw Δρ；缺 `data/sft_paired` → 阶段 2 行 pending 并印重建命令；`--tokenizer none` 跳过 token 计数。规则与冻结见 e3_plan §3。

## 7. SLURM（HAIC）

`slurm/train.sbatch`、`slurm/eval.sbatch` 用下表占位；**用户提交前确认 partition / account / QoS**（来自 2026-08 实测的 HAIC 手册，可能已变）。

| 项 | 值 | 备注 |
|---|---|---|
| `--account` | `ingrai` | 必带 |
| `--partition` | `hai`（批处理）；调试 `hai-interactive`；备胎 `hai-lo`（可抢占，别放长任务） | QoS 名未知：`sacctmgr show user $USER withassoc format=user,account%20,qos%30` 查，被拒再加 `--qos` |
| `--gres` | `gpu:h100:1`；`-c 8 --mem 64G` | 8B（E8）用 `gpu:h100:2` |
| `--time` | train `02:00:00`（预估 25–40 min × 1.15 + 保存）；eval `00:30:00` | |
| `--exclude` | `haic-hgx-2` | NFS 黑洞节点 |
| 环境 | **无 module、无 conda**：`cd /hai/scratch/$USER/CS329X_Project && source .venv/bin/activate`；venv 用 uv 装，torch 的 CUDA 版本不能高于节点驱动（haic-hgx-4 是 CUDA 12.4 → `torch==2.6.0` cu124 wheel）；vLLM 单独一个 `.venv-vllm`（`vllm==0.8.5.post1`）。见 `slurm/README.md` §0 | 验证只在计算节点 `python -c "import torch;print(torch.cuda.is_available())"` |
| 缓存 | `export HF_HOME=/hai/scratch/$USER/hf HF_HUB_OFFLINE=1`；Qwen3-4B-Base 在登录节点先 `huggingface-cli download` | 家目录 50 GB，全放 scratch |
| 日志 | `logs/%x-%j.out`（array task 也用 %j，每个 task 的 job id 唯一）；**logs/ 必须在提交前存在、从仓库根提交**：SLURM 在脚本运行前就打开日志文件 | |
| 显存 | `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`（sbatch 里导出）；gate run 看 manifest `peak_memory_gib` ≤ 70 再放网格 | |
| train 参数 | `sbatch slurm/train.sbatch <teacher> <version> <seed>` → 调 `11_train_student.py --data data/sft/{teacher}_{version}_s{seed}.jsonl --run-dir runs/qwen3-4b/{teacher}_{version}_s{seed} --seed {seed}`；已存在 `train_manifest.json` 则跳过 | 48 个 run 用 `--array=0-47%8` 映射到 (teacher, version, seed) 网格也可 |
| eval 参数 | `sbatch slurm/eval.sbatch <run-dir> <split>` → `12_eval_student.py --backend vllm`；vLLM 只装在集群 venv（`uv pip install -e ".[eval]"`） | 依赖链：`sbatch --dependency=afterok:$TRAIN slurm/eval.sbatch ...` |
| 头节点 | 禁一切计算，包括 pytest 与 `10_build_sft_data.py`（后者在本机 Mac 跑完 rsync 上去即可） | |

`slurm/README.md`（TRAIN 写）：以上命令 + 守门员模式（先 1 个 tiny / 1 个真实 run 过 `pytest -q` 再放网格）+ 同一 run-dir 禁止重复提交。

## 8. 测试契约

| 测试 | 覆盖 | 数据 |
|---|---|---|
| `tests/test_train_data.py` | template 字串、`canonical_target` 去尾随空格、边界（`text_target[0]==" "`）、order policy 的确定性、paired 交集、同 seed 下 O / F / C family 顺序相同、R 字母均衡 | `data/prompts/pilot_prompts_v2.jsonl` + `data/teacher_v2/{gpt4o,claude46}_demo.jsonl` + `data/rewrites_v9/*`；写到 `tmp_path` |
| `tests/test_sft_smoke.py`（`@pytest.mark.slow`，默认仍跑） | tiny profile 2 步：label mask 正确（prompt 位置 -100、target 与 EOS 非 -100）、manifest 字段齐、checkpoint 可被 `AutoModelForCausalLM` 重新加载 | 从 pilot 建 8 条 |
| `tests/test_readout.py` | `letter_token_ids` 在 SmolLM2 上得 `{A:[330,49], B:[389,50]}`；`readout_rows` 对手造分布给出正确 `p_letters` / `category` / `usage.top1`；transformers 后端在 tiny 模型上产出可被 `responses_to_frame → symmetrize` 消费的行 | SmolLM2 |
| `tests/test_e1_metrics.py` | 用手造 `sym` 表：agreement / JSD 已知值、`inheritance` 在学生 = teacher 时 Δρ > 0 且 p 小、`seed_noise_null` 的对数、`parse_run_id` | 无文件 |
| `tests/test_e3_metrics.py` | 合成 3 teacher × 3 seed × O / F / C 学生（F 加大噪声改变一致性 / agreement / 继承，C 为干净复制；另一世界 C 同质化）：规则 7 的 effect / no effect / inconclusive / pending（含 teacher < 3）、null 尺度匹配（q95 = t × RMS / √n_seeds）、iid H0 下每 teacher 超阈率 ≈ 5%、excess 分歧与 jackknife、seed-pair null 对数、分歧计数与 tie 排除、homogenization 方向与校准列、`inheritance_by_form`（partial 与 raw）、每版本 D 与 s（版本顺序无关）；合成 SFT + rewrites 树上的内容 / register 检查（LOO 无泄漏对照暴力循环、Wilson CI）；`scripts/15` 的三个 subprocess 冒烟（O / F / C 全网格、只有 O → 全 pending、只有一个 teacher 有 F / C → pending (n_teachers 1 < 3)） | 无文件 |

新测试必须在 CPU 上 < 60 s；既有 39 个测试不改。另有 scripts/12 与 13 的 subprocess 测试（tiny 基座在 pilot 上全 malformed；合成 runs/ 树出完整 summary、`_smoke_*` 目录被跳过）、训练首个 target token ∈ readout 字母 id 的跨模块断言、空版本 / 静默覆盖的拒绝、`load_train_yaml` 不碰 .env。

## 9. 如何跑

本机（Mac，CPU；约 1 分钟）：

```bash
.venv/bin/python -m pytest -q                                   # 全部测试，含 slow smoke
S=/tmp/vcd_smoke
.venv/bin/python scripts/10_build_sft_data.py --teacher gpt4o --versions O --seeds 1 \
    --prompts data/prompts/pilot_prompts_v2.jsonl --demos data/teacher_v2/gpt4o_demo.jsonl --out-dir $S/sft
head -8 $S/sft/gpt4o_O_s1.jsonl > $S/sft/pilot8.jsonl
HF_HUB_OFFLINE=1 .venv/bin/python scripts/11_train_student.py --data $S/sft/pilot8.jsonl \
    --out $S/runs/smollm2-135m/gpt4o_O_s1 --seed 1 --profile tiny --max-steps 2
HF_HUB_OFFLINE=1 .venv/bin/python scripts/12_eval_student.py --run-dir $S/runs/smollm2-135m/gpt4o_O_s1 \
    --split pilot --limit 8 --backend transformers --profile tiny          # 期望：tiny 模型全 malformed
.venv/bin/python scripts/13_e1_analysis.py --runs-dir $S/runs --student smollm2-135m --split pilot \
    --teacher-files gpt4o=data/teacher_v2/gpt4o_profile.jsonl,deepseek_v4=data/teacher_v2/deepseek_v4_profile.jsonl \
    --n-perm 200 --n-boot 200 --out $S/e1                                   # summary 说明全 malformed，不是"没有 run"
```

HAIC 核心网格（48 run）。前置：Phase 1 的 `data/teacher_phase1/*_train_demo.jsonl` 齐、F / C 的 train 集改写在 `data/rewrites_v9/{teacher}/rewrites.jsonl`；`slurm/README.md` §0 装好 venv（cu128 torch）并下载 Qwen3-4B-Base；提交前确认 account / partition / QoS。

```bash
# 1. Mac：建 SFT 文件（O 先建；F / C 与 O 同 teacher 一次建齐才 paired）
for t in gpt4o claude46 deepseek_v4; do
  .venv/bin/python scripts/10_build_sft_data.py --teacher $t --versions O,F,C --seeds 1,2,3,4,5 --tokenizer Qwen/Qwen3-4B-Base
done
.venv/bin/python scripts/10_build_sft_data.py --random-label --ref-teacher gpt4o --seeds 1,2,3
rsync -a data/sft/ haic:/hai/scratch/$USER/CS329X_Project/data/sft/
# 改写还没齐时只建 O：--versions O；之后 --versions O,F,C --overwrite 重建（O 文件内容不变，只是 prompt 集按交集收缩）

# 2. HAIC：gate run（slurm/README.md §1：pytest + 30 步真模型 + vLLM/transformers 一致性 + peak_memory_gib ≤ 70），然后网格
cd /hai/scratch/$USER/CS329X_Project && mkdir -p logs runs
sbatch --array=0-47%8 slurm/train.sbatch                        # 48 run；只建了 O+R 时 --array=0-4,15-19,30-34,45-47%8
MODEL=Qwen/Qwen3-4B-Base sbatch slurm/eval.sbatch - dev; MODEL=Qwen/Qwen3-4B-Base sbatch slurm/eval.sbatch - test   # S_0 基座
for d in runs/qwen3-4b/*_s[1-5]; do for s in dev test; do sbatch slurm/eval.sbatch $d $s; done; done   # 训练完成后（已有 responses 的会跳过）

# 3. Mac：拉回 eval 结果（不拉 checkpoint），出表
rsync -a --include='*/' --include='eval/**' --include='train_manifest.json' --include='train_log.jsonl' --exclude='*' haic:/hai/scratch/$USER/CS329X_Project/runs/ runs/
.venv/bin/python scripts/13_e1_analysis.py --runs-dir runs --student qwen3-4b --split dev  --out results/e1_dev
.venv/bin/python scripts/13_e1_analysis.py --runs-dir runs --student qwen3-4b --split test --out results/e1   # 只在 dev 规则冻结后跑一次
```
