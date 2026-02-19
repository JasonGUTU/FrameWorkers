# Agents Directory Migration & Frameworks Backend Renaming

## 更改总结

### 1. Agents 目录迁移到项目根目录 ✅

**之前的结构：**
```
FrameWorkers/
├── dynamic-task-stack/
│   └── src/
│       └── assistant/
│           └── agents/        # Agents 在这里（太深）
│               └── example_agent/
```

**现在的结构：**
```
FrameWorkers/
├── agents/                     # ✅ Agents 在根目录（易于访问）
│   ├── __init__.py
│   ├── base_agent.py          # 导入辅助模块
│   ├── README.md
│   └── example_agent/
│       ├── __init__.py
│       └── agent.py
├── dynamic-task-stack/
│   └── src/
│       └── assistant/
│           └── agents/        # 保留用于向后兼容
│               └── ...
```

### 2. 命名更新：Dynamic Task Stack → Frameworks Backend ✅

所有相关文件中的命名已更新：
- `src/app.py` - 主应用注释
- `src/task_stack/routes.py` - API 路由注释和健康检查响应
- `src/task_stack/storage.py` - 存储模块注释
- `src/task_stack/models.py` - 模型模块注释
- `src/__init__.py` - 包注释

### 3. Agent 发现机制更新 ✅

`AgentRegistry` 现在：
1. **优先查找根目录的 agents 文件夹**
2. 如果根目录存在 `agents/`，则使用它
3. 否则回退到 `src/assistant/agents/`（向后兼容）

### 4. 导入辅助模块 ✅

创建了 `agents/base_agent.py` 辅助模块：
- 自动添加 backend 路径到 sys.path
- 提供简单的导入接口：`from ..base_agent import BaseAgent`
- 让根目录的 agents 可以轻松导入 BaseAgent

## 使用指南

### 创建新 Agent

1. **在根目录的 agents 文件夹下创建新目录：**
   ```bash
   cd /Users/jinjingu/Documents/Projects/FrameWorkers
   mkdir agents/my_new_agent
   ```

2. **创建 agent.py：**
   ```python
   from typing import Dict, Any
   from datetime import datetime
   from ..base_agent import BaseAgent, AgentMetadata

   class MyNewAgent(BaseAgent):
       def get_metadata(self) -> AgentMetadata:
           return AgentMetadata(
               id="my_new_agent",
               name="My New Agent",
               description="Description here",
               capabilities=["capability1"],
               input_schema={
                   "input": {"type": "string", "required": True}
               },
               output_schema={
                   "result": {"type": "string"}
               }
           )
       
       def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
           self.validate_inputs(inputs)
           # Your logic here
           return {"result": "processed"}
   ```

3. **创建 __init__.py：**
   ```python
   from .agent import MyNewAgent
   __all__ = ['MyNewAgent']
   ```

4. **Agent 会自动被发现和注册！**

### 优势

✅ **易于访问**：Agents 在项目根目录，路径短，易于找到和修改  
✅ **分离关注点**：Agents 与 backend 代码分离  
✅ **向后兼容**：旧的 agents 目录仍然可以工作  
✅ **自动发现**：无需手动配置，启动时自动注册  

## API 端点

所有 API 端点保持不变：
- `GET /api/assistant/sub-agents` - 获取所有已安装的 agents（聚合信息）
- `GET /api/assistant/sub-agents/<agent_id>` - 获取特定 agent 信息
- `POST /api/assistant/execute` - 执行 agent

## 注意事项

1. **导入路径**：根目录的 agents 使用 `from ..base_agent import BaseAgent`
2. **自动发现**：AgentRegistry 会自动扫描根目录的 agents 文件夹
3. **向后兼容**：如果根目录没有 agents 文件夹，会回退到旧的路径
