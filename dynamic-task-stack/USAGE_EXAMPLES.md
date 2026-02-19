# Dynamic Task Stack 使用示例

## 系统概述

Dynamic Task Stack 是一个分层级的任务执行系统，支持：
- 分层级任务管理（Layer-based task management）
- 每层执行前后的 Hook（Pre-hook 和 Post-hook）
- 执行指针跟踪当前执行位置
- 动态修改未执行的任务（原子操作）

**重要原则：已执行的任务不能被修改，只能修改未执行的任务。**

## 基本使用流程

### 1. 创建任务栈结构

#### 步骤 1: 创建第一层
```bash
POST /api/layers
Content-Type: application/json

{
  "pre_hook": {
    "type": "middleware",
    "action": "prepare_environment",
    "config": {}
  },
  "post_hook": {
    "type": "hook",
    "action": "cleanup",
    "config": {}
  }
}
```

响应：
```json
{
  "layer_index": 0,
  "tasks": [],
  "pre_hook": {...},
  "post_hook": {...},
  "created_at": "2024-01-01T10:00:00"
}
```

#### 步骤 2: 创建任务
```bash
POST /api/tasks
Content-Type: application/json

{
  "description": {
    "overall_description": "处理用户输入数据",
    "input": {"data": "example"},
    "requirements": ["validate", "transform"],
    "additional_notes": "需要特殊处理"
  }
}
```

响应：
```json
{
  "id": "task_1_abc123",
  "description": {...},
  "status": "PENDING",
  "progress": {},
  "results": null,
  "created_at": "2024-01-01T10:00:01",
  "updated_at": "2024-01-01T10:00:01"
}
```

#### 步骤 3: 将任务添加到第一层
```bash
POST /api/layers/0/tasks
Content-Type: application/json

{
  "task_id": "task_1_abc123"
}
```

#### 步骤 4: 创建第二层并添加任务
```bash
# 创建第二层
POST /api/layers
{
  "pre_hook": {"type": "middleware", "action": "prepare"},
  "post_hook": {"type": "hook", "action": "finalize"}
}

# 创建任务
POST /api/tasks
{
  "description": {
    "overall_description": "执行数据分析",
    "input": {},
    "requirements": ["analyze"],
    "additional_notes": ""
  }
}

# 添加任务到第二层
POST /api/layers/1/tasks
{
  "task_id": "task_2_def456"
}

# 再添加一个任务到第二层
POST /api/tasks
{
  "description": {
    "overall_description": "生成报告",
    "input": {},
    "requirements": ["generate"],
    "additional_notes": ""
  }
}

POST /api/layers/1/tasks
{
  "task_id": "task_3_ghi789"
}
```

### 2. 执行任务栈

#### 步骤 1: 设置执行指针（从第一层第一个任务开始）
```bash
PUT /api/execution-pointer
Content-Type: application/json

{
  "layer_index": 0,
  "task_index": 0,
  "is_executing_pre_hook": false,
  "is_executing_post_hook": false
}
```

#### 步骤 2: 获取下一个要执行的任务
```bash
GET /api/task-stack/next
```

响应：
```json
{
  "layer_index": 0,
  "task_index": 0,
  "task_id": "task_1_abc123",
  "task": {...},
  "layer": {
    "layer_index": 0,
    "tasks": [...],
    "pre_hook": {...},
    "post_hook": {...}
  },
  "is_pre_hook": false
}
```

#### 步骤 3: 执行流程
1. **执行 Pre-hook**（如果存在且未执行）
   - 设置 `is_executing_pre_hook: true`
   - 执行 pre-hook 逻辑
   - 设置 `is_executing_pre_hook: false`

2. **执行任务**
   - 更新任务状态为 `IN_PROGRESS`
   - 执行任务逻辑
   - 更新任务状态为 `COMPLETED` 或 `FAILED`
   - 更新任务的 `results` 和 `progress`

3. **推进执行指针**
   ```bash
   POST /api/execution-pointer/advance
   ```

4. **执行 Post-hook**（如果当前层的所有任务都完成）
   - 设置 `is_executing_post_hook: true`
   - 执行 post-hook 逻辑
   - 设置 `is_executing_post_hook: false`

### 3. 动态修改任务栈

**重要：只能修改未执行的任务！**

#### 场景：替换任务（原子操作）

假设当前执行指针在 Layer 0, Task 0，我们想替换 Layer 1 中的某个任务：

```bash
# 1. 创建新任务
POST /api/tasks
{
  "description": {
    "overall_description": "新的任务描述",
    "input": {},
    "requirements": [],
    "additional_notes": ""
  }
}
# 返回: task_4_jkl012

# 2. 原子替换：取消旧任务，添加新任务
POST /api/layers/1/tasks/replace
Content-Type: application/json

{
  "old_task_id": "task_2_def456",
  "new_task_id": "task_4_jkl012"
}
```

这个操作会：
- 自动将 `task_2_def456` 的状态设置为 `CANCELLED`
- 在同一位置用 `task_4_jkl012` 替换它
- 这是一个原子操作，要么全部成功，要么全部失败

#### 场景：删除未执行的任务

```bash
DELETE /api/layers/1/tasks/task_3_ghi789
```

**注意**：如果任务已经执行，这个操作会失败并返回错误。

#### 场景：添加新任务到未执行的层

```bash
# 创建新任务
POST /api/tasks
{
  "description": {...}
}
# 返回: task_5_mno345

# 添加到第二层（如果第二层还未执行）
POST /api/layers/1/tasks
{
  "task_id": "task_5_mno345",
  "insert_index": 1  # 可选：指定插入位置
}
```

#### 场景：在已执行层之后插入新层

```bash
# 假设当前执行到 Layer 1，我们想在 Layer 2 位置插入新层
POST /api/layers
{
  "layer_index": 2,
  "pre_hook": {...},
  "post_hook": {...}
}

# 添加任务到新层
POST /api/tasks
{
  "description": {...}
}

POST /api/layers/2/tasks
{
  "task_id": "task_6_pqr678"
}
```

### 4. 查询操作

#### 获取所有层
```bash
GET /api/layers
```

#### 获取特定层
```bash
GET /api/layers/0
```

#### 获取当前执行指针
```bash
GET /api/execution-pointer
```

#### 获取所有任务
```bash
GET /api/tasks
```

#### 获取特定任务
```bash
GET /api/tasks/task_1_abc123
```

### 5. 更新操作

#### 更新任务状态
```bash
PUT /api/tasks/task_1_abc123
Content-Type: application/json

{
  "status": "COMPLETED",
  "progress": {
    "step1": "done",
    "step2": "done"
  },
  "results": {
    "output": "processed_data",
    "metadata": {}
  }
}
```

#### 更新层的 Hook
```bash
PUT /api/layers/0/hooks
Content-Type: application/json

{
  "pre_hook": {
    "type": "updated_middleware",
    "action": "new_prepare"
  }
}
```

**注意**：如果层已经执行，更新 Hook 会失败。

## 完整示例：典型工作流

```python
# 1. 初始化任务栈
# 创建第一层
layer0 = create_layer(pre_hook={...}, post_hook={...})

# 创建并添加任务
task1 = create_task(description={...})
add_task_to_layer(0, task1.id)

# 创建第二层
layer1 = create_layer(pre_hook={...}, post_hook={...})

# 创建并添加多个任务
task2 = create_task(description={...})
task3 = create_task(description={...})
add_task_to_layer(1, task2.id)
add_task_to_layer(1, task3.id)

# 2. 开始执行
set_execution_pointer(0, 0)

# 3. 执行循环
while True:
    next_task_info = get_next_task()
    if not next_task_info:
        break
    
    # 执行 pre-hook（如果需要）
    if next_task_info['is_pre_hook']:
        execute_pre_hook(next_task_info['layer'])
    
    # 执行任务
    task = get_task(next_task_info['task_id'])
    result = execute_task(task)
    update_task(task.id, status="COMPLETED", results=result)
    
    # 推进指针
    advance_execution_pointer()
    
    # 检查是否需要执行 post-hook
    # （当前层所有任务完成时）

# 4. 动态修改（在执行过程中）
# 假设执行到 Layer 0 完成，发现 Layer 1 需要修改

# 替换任务
replace_task_in_layer(
    layer_index=1,
    old_task_id=task2.id,
    new_task_id=new_task.id
)

# 继续执行...
```

## 错误处理

### 常见错误

1. **尝试修改已执行的任务**
   ```
   Error: Task has already been executed
   ```
   解决：只能修改执行指针之后的任务

2. **尝试删除已执行的层**
   ```
   Error: Layer has already been executed
   ```
   解决：系统不支持删除层，只能修改层内的任务

3. **无效的执行指针位置**
   ```
   Error: Invalid layer_index or task_index
   ```
   解决：确保 layer_index 和 task_index 在有效范围内

## 注意事项

1. **执行顺序**：严格按照层级顺序执行（Layer 0 → Layer 1 → Layer 2 → ...）
2. **任务状态**：任务状态只能向前推进（PENDING → IN_PROGRESS → COMPLETED/FAILED）
3. **原子操作**：`replace_task_in_layer` 是原子操作，确保数据一致性
4. **线程安全**：所有操作都是线程安全的，支持并发访问
5. **执行指针**：执行指针是全局的，用于跟踪整个任务栈的执行进度
