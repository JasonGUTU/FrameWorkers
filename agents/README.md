# Agents 开发指南

本文档详细说明如何创建、开发和部署 Agent 到 Frameworks Backend。

**重要说明：**
- `agents/`（根目录）：实际 Agent 实现的位置，每个 Agent 放在独立的子目录中
- `assistant/agent_core/`（backend 内部）：Agent 核心框架，包含 BaseAgent 基类和注册机制

## 目录

- [概述](#概述)
- [目录结构](#目录结构)
- [创建新 Agent - 详细步骤](#创建新-agent---详细步骤)
- [Agent 实现规范](#agent-实现规范)
- [输入输出模式定义](#输入输出模式定义)
- [Agent 自动发现机制](#agent-自动发现机制)
- [测试和调试](#测试和调试)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 概述

Agent 是 Frameworks Backend 中的核心功能单元，每个 Agent 负责实现特定的功能。Agent 系统具有以下特点：

- ✅ **自动发现**：Agent 会在应用启动时自动被发现和注册
- ✅ **易于开发**：只需继承 `BaseAgent` 并实现两个方法
- ✅ **统一管理**：通过 Assistant 系统统一管理和执行
- ✅ **独立部署**：Agent 位于项目根目录，易于访问和修改

---

## 目录结构

每个 Agent 必须放在独立的文件夹中：

```
agents/
├── __init__.py                  # Agents 模块初始化
├── base_agent.py                # BaseAgent 导入辅助模块（不要修改）
├── README.md                    # 本文档
├── example_agent/                # 示例 Agent（参考实现）
│   ├── __init__.py              # 导出 Agent 类
│   └── agent.py                 # Agent 实现
└── your_agent/                   # 你的 Agent
    ├── __init__.py
    └── agent.py
```

---

## 创建新 Agent - 详细步骤

### 步骤 1: 创建 Agent 目录

在项目根目录的 `agents/` 文件夹下创建新目录：

```bash
# 进入项目根目录
cd /Users/jinjingu/Documents/Projects/FrameWorkers

# 创建 Agent 目录（使用下划线命名）
mkdir agents/storyboard_agent
```

**注意事项：**
- 目录名使用下划线命名（snake_case），如 `storyboard_agent`、`transcript_agent`
- 目录名应该清晰描述 Agent 的功能
- 避免使用特殊字符和空格

### 步骤 2: 创建 agent.py 文件

在 Agent 目录下创建 `agent.py` 文件：

```bash
cd agents/storyboard_agent
touch agent.py
```

### 步骤 3: 实现 Agent 类

编辑 `agent.py`，实现 Agent 类：

```python
# agents/storyboard_agent/agent.py

from typing import Dict, Any
from datetime import datetime

# 导入 BaseAgent 和 AgentMetadata
from ..base_agent import BaseAgent, AgentMetadata


class StoryboardAgent(BaseAgent):
    """
    Storyboard Agent - 生成视频项目的故事板
    
    这个 Agent 接收脚本和样式参数，生成对应的故事板。
    """
    
    def get_metadata(self) -> AgentMetadata:
        """
        返回 Agent 的元数据
        
        这个方法定义了 Agent 的基本信息、能力和输入输出模式。
        """
        return AgentMetadata(
            # Agent 唯一标识符（必须与目录名保持一致）
            id="storyboard_agent",
            
            # Agent 显示名称
            name="Storyboard Agent",
            
            # Agent 描述
            description="Creates storyboards for video projects based on scripts",
            
            # 版本号（可选）
            version="1.0.0",
            
            # 作者（可选）
            author="Your Name",
            
            # Agent 能力列表（可选，用于分类和搜索）
            capabilities=[
                "storyboard_generation",
                "visual_design",
                "video_production"
            ],
            
            # 输入模式定义（必须）
            input_schema={
                "script": {
                    "type": "string",
                    "required": True,
                    "description": "Video script content"
                },
                "style": {
                    "type": "string",
                    "required": False,
                    "description": "Visual style preference",
                    "default": "default"
                },
                "frame_count": {
                    "type": "number",
                    "required": False,
                    "description": "Number of storyboard frames",
                    "default": 10
                }
            },
            
            # 输出模式定义（可选，但推荐）
            output_schema={
                "storyboard": {
                    "type": "array",
                    "description": "List of storyboard frames",
                    "items": {
                        "type": "object",
                        "properties": {
                            "frame_number": {"type": "number"},
                            "description": {"type": "string"},
                            "visual_elements": {"type": "array"}
                        }
                    }
                },
                "status": {
                    "type": "string",
                    "description": "Generation status"
                }
            }
        )
    
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行 Agent 的核心逻辑
        
        Args:
            inputs: 输入数据字典，包含：
                - script: 视频脚本（必需）
                - style: 视觉样式（可选）
                - frame_count: 帧数（可选）
        
        Returns:
            包含执行结果的字典：
                - storyboard: 故事板数组
                - status: 执行状态
        
        Raises:
            ValueError: 如果输入无效
            RuntimeError: 如果执行失败
        """
        # 步骤 1: 验证输入（推荐）
        self.validate_inputs(inputs)
        
        # 步骤 2: 提取输入参数
        script = inputs.get("script", "")
        style = inputs.get("style", "default")
        frame_count = inputs.get("frame_count", 10)
        
        # 步骤 3: 验证必需参数
        if not script:
            raise ValueError("script is required")
        
        # 步骤 4: 实现核心逻辑
        # 这里是你实际的业务逻辑
        storyboard = []
        for i in range(frame_count):
            frame = {
                "frame_number": i + 1,
                "description": f"Frame {i + 1} based on script",
                "visual_elements": [
                    f"Element from script: {script[:50]}...",
                    f"Style: {style}"
                ]
            }
            storyboard.append(frame)
        
        # 步骤 5: 返回结果
        return {
            "storyboard": storyboard,
            "status": "completed",
            "frame_count": len(storyboard),
            "style_used": style,
            "timestamp": datetime.now().isoformat()
        }
```

### 步骤 4: 创建 __init__.py 文件

创建 `__init__.py` 文件以导出 Agent 类：

```bash
touch __init__.py
```

编辑 `__init__.py`：

```python
# agents/storyboard_agent/__init__.py

from .agent import StoryboardAgent

__all__ = ['StoryboardAgent']
```

**注意事项：**
- `__init__.py` 必须导出 Agent 类
- 类名使用驼峰命名（PascalCase）
- `__all__` 列表包含所有导出的类

### 步骤 5: 验证 Agent

重启 Backend 服务，Agent 会自动被发现和注册：

```bash
# 重启服务
cd dynamic-task-stack
python run.py
```

检查 Agent 是否成功注册：

```bash
# 查询所有已安装的 agents
curl http://localhost:5000/api/assistant/sub-agents

# 查询特定 agent
curl http://localhost:5000/api/assistant/sub-agents/storyboard_agent
```

### 步骤 6: 测试 Agent

通过 API 测试 Agent：

```bash
# 创建 assistant（如果还没有）
curl -X POST http://localhost:5000/api/assistant/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Assistant",
    "description": "Test assistant",
    "agent_ids": ["storyboard_agent"]
  }'

# 创建任务
curl -X POST http://localhost:5000/api/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "description": {
      "overall_description": "Test task"
    }
  }'

# 执行 Agent
curl -X POST http://localhost:5000/api/assistant/execute \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "assistant_1_xxx",
    "agent_id": "storyboard_agent",
    "task_id": "task_1_xxx",
    "additional_inputs": {
      "script": "This is a test script",
      "style": "modern",
      "frame_count": 5
    }
  }'
```

---

## Agent 实现规范

### 必须实现的方法

#### 1. `get_metadata() -> AgentMetadata`

返回 Agent 的元数据，包括：
- `id`: Agent 唯一标识符（必须与目录名一致）
- `name`: Agent 显示名称
- `description`: Agent 描述
- `capabilities`: 能力列表（可选）
- `input_schema`: 输入模式定义（必须）
- `output_schema`: 输出模式定义（推荐）

#### 2. `execute(inputs: Dict[str, Any]) -> Dict[str, Any]`

执行 Agent 的核心逻辑：
- 接收输入数据字典
- 验证输入（推荐使用 `self.validate_inputs()`）
- 实现业务逻辑
- 返回结果字典

### 可选方法

#### `validate_inputs(inputs: Dict[str, Any]) -> bool`

验证输入数据是否符合 `input_schema`。BaseAgent 提供了默认实现，但你可以覆盖它以提供自定义验证。

---

## 输入输出模式定义

### 输入模式 (input_schema)

定义 Agent 接受的输入参数：

```python
input_schema = {
    "field_name": {
        "type": "string" | "number" | "boolean" | "object" | "array",
        "required": True | False,              # 是否必需
        "description": "Field description",     # 字段描述
        "default": default_value,              # 默认值（可选）
        "enum": [value1, value2],              # 枚举值（可选）
        "items": {...}                         # 当 type="array" 时使用
    }
}
```

**示例：**

```python
input_schema = {
    "text": {
        "type": "string",
        "required": True,
        "description": "Text to process"
    },
    "language": {
        "type": "string",
        "required": False,
        "description": "Language code",
        "default": "en",
        "enum": ["en", "zh", "ja"]
    },
    "options": {
        "type": "object",
        "required": False,
        "description": "Additional options",
        "properties": {
            "format": {"type": "string"},
            "quality": {"type": "number"}
        }
    },
    "tags": {
        "type": "array",
        "required": False,
        "description": "Tags list",
        "items": {"type": "string"}
    }
}
```

### 输出模式 (output_schema)

定义 Agent 返回的输出结构：

```python
output_schema = {
    "result": {
        "type": "string",
        "description": "Result description"
    }
}
```

**示例：**

```python
output_schema = {
    "result": {
        "type": "string",
        "description": "Processed result"
    },
    "metadata": {
        "type": "object",
        "description": "Additional metadata",
        "properties": {
            "processing_time": {"type": "number"},
            "confidence": {"type": "number"}
        }
    },
    "items": {
        "type": "array",
        "description": "List of items",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "value": {"type": "string"}
            }
        }
    }
}
```

---

## Agent 自动发现机制

### 工作原理

1. **启动时扫描**：Backend 启动时，`AgentRegistry` 会自动扫描 `agents/` 目录
2. **加载 Agent**：对于每个子目录，尝试导入并实例化 Agent 类
3. **注册 Agent**：将成功加载的 Agent 注册到全局 registry
4. **错误处理**：如果某个 Agent 加载失败，会记录警告但不会影响其他 Agent

### 目录要求

- Agent 必须放在 `agents/` 目录的子目录中
- 子目录名不能以 `_` 或 `.` 开头（会被忽略）
- 必须包含 `agent.py` 或 `__init__.py` 文件
- Agent 类必须继承 `BaseAgent`

### 验证 Agent 是否被发现

```bash
# 查询所有 agents
curl http://localhost:5000/api/assistant/sub-agents

# 响应示例
{
  "total_agents": 2,
  "agents": [
    {
      "id": "storyboard_agent",
      "name": "Storyboard Agent",
      "description": "...",
      "capabilities": [...],
      "input_schema": {...},
      "output_schema": {...}
    }
  ],
  "all_capabilities": [...],
  "agent_ids": ["storyboard_agent", "example_agent"]
}
```

---

## 测试和调试

### 单元测试

为 Agent 编写单元测试：

```python
# tests/test_storyboard_agent.py

import unittest
from agents.storyboard_agent.agent import StoryboardAgent


class TestStoryboardAgent(unittest.TestCase):
    
    def setUp(self):
        self.agent = StoryboardAgent()
    
    def test_get_metadata(self):
        metadata = self.agent.get_metadata()
        self.assertEqual(metadata.id, "storyboard_agent")
        self.assertIn("storyboard_generation", metadata.capabilities)
    
    def test_execute_with_valid_input(self):
        inputs = {
            "script": "Test script",
            "style": "modern",
            "frame_count": 3
        }
        result = self.agent.execute(inputs)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(result["storyboard"]), 3)
    
    def test_execute_with_missing_required_input(self):
        inputs = {}  # Missing required "script"
        with self.assertRaises(ValueError):
            self.agent.execute(inputs)
    
    def test_validate_inputs(self):
        inputs = {"script": "Test"}
        self.assertTrue(self.agent.validate_inputs(inputs))
```

### 调试技巧

1. **查看日志**：Backend 启动时会输出 Agent 加载日志
2. **检查导入**：确保 `from ..base_agent import BaseAgent` 正确
3. **验证元数据**：使用 API 查询 Agent 信息，检查元数据是否正确
4. **测试执行**：使用 API 直接执行 Agent，查看错误信息

---

## 最佳实践

### 1. 命名规范

- **目录名**：使用下划线命名（snake_case），如 `storyboard_agent`
- **Agent ID**：与目录名保持一致
- **类名**：使用驼峰命名（PascalCase），如 `StoryboardAgent`
- **文件名**：使用下划线命名，如 `agent.py`

### 2. 错误处理

```python
def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # 验证输入
        self.validate_inputs(inputs)
        
        # 实现逻辑
        result = self._process(inputs)
        
        return result
    except ValueError as e:
        # 输入错误
        raise ValueError(f"Invalid input: {e}")
    except Exception as e:
        # 其他错误
        raise RuntimeError(f"Execution failed: {e}")
```

### 3. 文档

- 为 Agent 类添加详细的 docstring
- 为每个输入输出字段添加描述
- 说明 Agent 的能力和用途
- 提供使用示例

### 4. 输入验证

```python
def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
    # 使用内置验证
    self.validate_inputs(inputs)
    
    # 额外的自定义验证
    script = inputs.get("script")
    if len(script) < 10:
        raise ValueError("Script must be at least 10 characters")
    
    # ...
```

### 5. 返回值规范

```python
def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
    # 返回结构化的结果
    return {
        "status": "completed",  # 或 "failed"
        "result": {...},        # 主要结果
        "metadata": {...},      # 元数据（可选）
        "timestamp": datetime.now().isoformat()  # 时间戳（推荐）
    }
```

---

## 常见问题

### Q1: Agent 没有被发现怎么办？

**检查清单：**
1. ✅ Agent 目录是否在 `agents/` 下？
2. ✅ 目录名是否以 `_` 或 `.` 开头？（会被忽略）
3. ✅ 是否包含 `agent.py` 或 `__init__.py`？
4. ✅ Agent 类是否继承 `BaseAgent`？
5. ✅ `__init__.py` 是否正确导出 Agent 类？
6. ✅ 导入路径是否正确：`from ..base_agent import BaseAgent`？

### Q2: 导入错误怎么办？

**解决方案：**
- 确保使用相对导入：`from ..base_agent import BaseAgent`
- 检查 `agents/base_agent.py` 文件是否存在
- 重启 Backend 服务

### Q3: 如何更新 Agent？

**步骤：**
1. 修改 `agent.py` 文件
2. 重启 Backend 服务
3. Agent 会自动重新加载

### Q4: 如何删除 Agent？

**步骤：**
1. 删除 Agent 目录
2. 重启 Backend 服务
3. Agent 会自动从 registry 中移除

### Q5: Agent 执行失败怎么办？

**调试步骤：**
1. 检查输入数据是否符合 `input_schema`
2. 查看 Backend 日志中的错误信息
3. 使用 API 直接测试 Agent 执行
4. 添加 try-catch 捕获具体错误

---

## 参考示例

参考 `example_agent/` 目录中的示例实现：

```bash
# 查看示例 Agent
cat agents/example_agent/agent.py
cat agents/example_agent/__init__.py
```

---

## 总结

创建 Agent 的完整流程：

1. ✅ 创建 Agent 目录
2. ✅ 实现 `agent.py`（继承 `BaseAgent`）
3. ✅ 实现 `get_metadata()` 方法
4. ✅ 实现 `execute()` 方法
5. ✅ 创建 `__init__.py` 导出类
6. ✅ 重启 Backend，Agent 自动注册
7. ✅ 通过 API 测试 Agent

遵循这些步骤，你就可以成功创建和部署 Agent！
