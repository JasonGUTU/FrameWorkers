# Spot check — 0 SFT + 0 DPO samples

**For each SFT sample, check:**
1. rationale 引用的规则在 descriptor 里存在吗？（不要胡编「根据 XXX 原则」）
2. rationale 的结论和 plan 一致吗？（rationale 说不加 X，plan 里就不该有 X）
3. intent 是否带上了 user_goal 的具体内容（不是模板化的「process the X」）

**For each DPO pair, check:**
1. chosen rationale 是否清晰拒绝了 rejected 引入的 bias
2. rejected rationale 是否「看似合理但显然错」（自洽但确实是错的推理）
3. 长度是否大致平衡（chosen vs rejected total assistant content 差距 < 15%）

---

# SFT samples

# DPO pairs
