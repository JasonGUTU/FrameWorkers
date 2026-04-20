# SFT 生成 hand-off（session 1 结束快照）

## 当前进度
- **SFT: 435 / 1090 (40%)**，0 transliteration/flip 违规
- **DPO: 0 / 500** (未开始)
- **文件**：
  - `training/director/samples_sft_full.jsonl` — 435 条
  - `training/director/samples_sft_full.jsonl.v622.bak` — 上一版 622 条（可弃）
  - `training/director/batches/batch_001…018_*.json` — 18 个 batch 源
- **eval baseline**：`Runtime/eval_routing/20260420_174738_english_flipped_baseline.json` (88% chain acc)

## 已完成 chain（= target）

| chain | target | done | batches |
|---|---|---|---|
| IntakeText→IntakeVideo→VideoExtend→Music→AudioMix→Compositor | 30 | 30 | 001 |
| IntakeText→IntakeVideo→VideoExtend | 50 | 50 | 002+003 |
| IntakeText→IntakeVideo→StyleTransfer | 50 | 50 | 004+005 |
| IntakeText→IntakeVideo→Music→AudioMix→Compositor | 30 | 30 | 006+007 |
| IntakeText→IntakeVideo→Ambience→Music→AudioMix→Compositor | 30 | 30 | 008+009 |
| IntakeText→IntakeVideo→VideoAnalysis→Highlight | 40 | 40 | 010+012 |
| IntakeText→IntakeVideo→Transcription→Subtitle→Compositor | 30 | 30 | 011+012 |
| IntakeText→IntakeVideo→VideoExtend→StyleTransfer | 30 | 30 | 013 |
| IntakeText→IntakeVideo→StyleTransfer→Music→AudioMix→Compositor | 30 | 30 | 015 |

## 部分填充 chain（差几条再凑整 target）

| chain | target | done | 缺 |
|---|---|---|---|
| IntakeText→IntakeVideo→VideoExtend→Transcription→Subtitle→Compositor | 30 | 28 | 2 |
| IntakeText→Story→Screenplay→KeyFrame→Video→Ambience→Music→AudioMix→Compositor (**Creative 核心，最大 bucket**) | 150 | 29 | **121** |
| IntakeText→IntakeVideo→Transcription→Subtitle→Translation→Compositor (**Translation 核心**) | 40 | 29 | 11 |
| IntakeText→IntakeVideo→StyleTransfer→Transcription→Subtitle→Compositor | 30 | 29 | 1 |

## 待完成 chain（15 个 chain 完全为 0，共 **495 条**）

| 优先级 | chain | target |
|---|---|---|
| P1 | IntakeText→Story→Screenplay→KeyFrame→Video→Ambience→Music→AudioMix→Subtitle→Compositor (len=10, Creative+subtitle) | 50 |
| P1 | IntakeText→Story→Screenplay→KeyFrame→Video→Ambience→Music→AudioMix→Subtitle→Translation→Compositor (len=11, Creative+bilingual) | 50 |
| P1 | IntakeText→IntakeImage→BriefEnricher→Story→Screenplay→KeyFrame→Video→Ambience→Music→AudioMix→Compositor (len=11, Image+Creative) | 50 |
| P2 | IntakeText→IntakeVideo→VideoAnalysis→Highlight→Music→Subtitle→AudioMix→Compositor (len=8) | 40 |
| P2 | IntakeText→IntakeVideo→VideoAnalysis→Highlight→Music→AudioMix→Compositor (len=7) | 30 |
| P2 | IntakeText→IntakeVideo→VideoAnalysis→Highlight→Transcription→Subtitle→Compositor (len=7) | 30 |
| P2 | IntakeText→IntakeVideo→VideoAnalysis→Highlight→Transcription→Subtitle→Compositor (len=8, 变种) | 30 |
| P2 | IntakeText→IntakeVideo→VideoAnalysis→Highlight→Transcription→Subtitle→Translation→Compositor (len=10) | 30 |
| P2 | IntakeText→IntakeVideo→Transcription→Subtitle→Music→AudioMix→Compositor (len=7) | 30 |
| P3 | IntakeText→IntakeVideo→VideoAnalysis→Story→Screenplay→KeyFrame→Video→Ambience→Music→AudioMix→Compositor (len=11) | 30 |
| P3 | IntakeText→IntakeVideo→VideoAnalysis→Story→Screenplay→KeyFrame→Video→Ambience→Music→AudioMix→Subtitle→Compositor (len=12) | 30 |
| P3 | IntakeText→IntakeVideo→VideoExtend→StyleTransfer→Transcription→Subtitle→Compositor (len=7) | 30 |
| P3 | IntakeText→IntakeVideo→StyleTransfer→VideoExtend→Music→AudioMix→Compositor (len=7) | 30 |
| P3 | IntakeText→IntakeImage→BriefEnricher→Story→Screenplay→KeyFrame→Video→VideoExtend→Ambience→Music→AudioMix→Compositor (len=12) | 30 |
| P3 | IntakeText→IntakeImage→BriefEnricher→Story→Screenplay→KeyFrame→Video→Ambience→Music→AudioMix→Subtitle→Translation→Compositor (len=13) | 30 |

## 约定（严格遵守）

### 词汇约定表（grep 违规零容忍）
```
修仙  → cultivation-fantasy    (不要 xianxia)
漫剧  → animated drama         (不要 manhua)
武侠  → martial-arts (drama)   (不要 wuxia)
短剧  → mini-drama
古装  → costume-drama
宫斗  → palace-intrigue
霸总  → CEO romance
重生  → rebirth
赘婿  → live-in son-in-law
中英双语 → English-Chinese bilingual  (English-first)
中文字幕 → English subtitles    (默认英文，跨语才 Translation)
竖屏  → (drop，不翻)
```

### 语言 flip 原则
- **FrameWorker 默认 source/output = English**
- "Add English subtitles to X" → 单语 → 无 Translation
- "Generate Chinese/Spanish/Japanese subtitles for English X" → 跨语 → **需要** Translation
- bilingual pair 英文先："English-Chinese bilingual"

### rationale 模板（必须显式反 4 种 bias）
```
User [uploaded/asks] ... Plan: IntakeText captures the brief, ... [agent-by-agent].
No VideoAnalysisAgent because ...     ← 若 VA 不在 chain
No MusicAgent because no score was requested.        ← 若 Music 不在
No AmbienceAgent because only a score was requested.  ← 若 Music 在但 Ambience 不在
No CompositorAgent because [Highlight/Extend/Style output is the deliverable directly].  ← 若 Compositor 不在
No SubtitleAgent or StyleTransferAgent because ...    ← catch-all
No TranslationAgent because source and subtitle languages match.  ← 若单语但有 Subtitle
```

### plan intent 约定
- 每个 agent 1 句 8-25 词 / 带 user_goal 具体内容
- **禁止模板化**（"step for MusicAgent"）

### user_goal
- 英文原生，非 CN→EN 翻译腔
- 3 要素：题材/素材 + 动作/目标 + 关键约束
- 不提触发其他 agent 的词
- **避免 eval_cases 里的原文字字重复**（`append-sft` 的 `_normalize_goal` 会拒绝撞车 goal）—— Creative 类 goal 尤其要重新组合 plot

## 工具链

```bash
source ~/.bashrc && conda activate frameworkers

# 查进度
PYTHONPATH=. python training/director/gen_by_hand.py progress

# eval 撞车预检
python3 -c "
import json, re
eval_cases = json.load(open('evals/director_routing/eval_cases.json'))
def norm(g): return re.sub(r'[\s,。,！!？?、；;：:.\"\\\'\\u2018\\u2019\\u201c\\u201d]+', '', (g or '').lower().strip())
eval_norms = {norm(c['user_goal']): c['name'] for c in eval_cases}
batch = json.load(open('PATH_TO_BATCH.json'))
for i, r in enumerate(batch, 1):
    hit = eval_norms.get(norm(r['goal']))
    if hit: print(f'#{i} conflicts with {hit}: {r[\"goal\"][:80]}')
"

# append 一批
PYTHONPATH=. python training/director/gen_by_hand.py append-sft training/director/batches/batch_NNN.json

# 违规 scan
python3 -c "
import json, re
rows = [json.loads(l) for l in open('training/director/samples_sft_full.jsonl')]
v = 0
for r in rows:
    full = r['messages'][1]['content'] + ' ' + json.loads(r['messages'][-1]['content'])['rationale']
    for p in [r'\bxianxia\b', r'\bwuxia\b', r'\bmanhua\b', r'\bvertical[-\s]?(screen|format)\b']:
        if re.search(p, full, re.I): v += 1
print(f'total: {len(rows)}  violations: {v}')
"
```

## 下次 session 启动 checklist
1. `progress` 看最新剩余 chain
2. 补前几批留的 patches：VideoExtend+Transcription+Subtitle 差 2 / StyleTransfer+Transcription+Subtitle 差 1 / Translation 差 11 / Creative 差 121
3. P1 优先（Creative 核心大 bucket，Image-based Creative 50）
4. 每批 append 前先跑 eval-撞车预检
5. 每批 append 后跑违规 scan
6. 每 ~100 条 spot check 抽 3 条（CN/EN goal 风格 + rationale bias coverage + IntakeTextAgent 是 plan[0]）

## 已知陷阱
- **Creative 类 user_goal 严重撞车 eval**：因为 eval 的 cr_*/sub_*/bilingual_* 等就是 creative prompt。写这类 batch 前必须用预检脚本。其他 chain（VideoExtend/StyleTransfer/etc）撞车率低得多，因为 eval 里相关 case 少。
- 每批我经常手滑少 1-3 条（30 写成 28/29）；不追平，留到最后统一 patch
- 英文 rationale 容易滑回带 xianxia/wuxia/manhua 音译 — 每批 append 后必跑违规 scan
- `append-sft` 遇 eval 撞车会 raise 并 **整批 reject**（不是跳过那一条）—— 必须所有条都预检通过

## 本 session 关键决策记录（供下次 session 快速理解语境）
- **eval 100 条从 CN 翻译到 EN**：`evals/director_routing/_translate_to_english.py` 存翻译映射（86 条），已同步 eval_cases.json / review_log.json / eval_cases.md。脚本一次性，用完可删
- **中英 flip**：user_goal 里 "Chinese subtitles" → "English subtitles"（默认 FrameWorker 输出英文）；Translation 方向倒置；bilingual pair 英文先。35 条被 flip，见 FLIP_LANG dict
- **eval baseline 翻译+flip 后 88%**（之前 82%），说明 flip 消除了大量隐性 drift
- **之前 622 条 samples 作废**：第一版（session 前）rationale 太浅，不反 bias。当前 435 条是完全重做版本，rationale 符合 CLAUDE.md 标准 80-600 字符 + 显式反 4 种 bias
