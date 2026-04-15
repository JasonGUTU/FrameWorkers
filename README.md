# FrameWorkers

任务编排 + 多模态 Agent 框架：Director 推理 → Task Stack 编排 → Assistant 执行 sub-agent 流水线 → Workspace 落盘。

> 架构、目录、约定见 [`CLAUDE.md`](./CLAUDE.md)（项目唯一权威说明）。

## Install

```bash
conda activate frameworkers
python install_requirements.py

cd interface && npm install
```

`install_requirements.py` 可重复执行；若 `frameworkers` 环境已存在会跳过创建，仅更新依赖。

## Run

```bash
# Backend (port 5002)
cd plan-stack-backend && python run.py

# Director (新终端)
cd director_agent && python run.py

# Frontend (新终端, port 3000)
cd interface && npm run dev
```

## Test

```bash
bash tests/run_core_tests.sh
```
