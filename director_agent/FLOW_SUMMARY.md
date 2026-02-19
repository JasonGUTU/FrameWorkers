# 流程图总结 (FlowChartDesign)

## 系统架构概述

本流程图描述了一个基于Agent的任务编排系统，包含以下主要组件：

1. **User (用户)** - 提供指令和接收信息更新
2. **Interface (接口)** - 用户交互界面，负责消息传递和信息展示
3. **Task Stack (任务栈)** - 管理任务队列和状态
4. **Director Agent (导演代理)** - 负责推理、规划和任务编排
5. **Assistant Agent (助手代理)** - 执行任务，协调子任务代理
6. **Subtask Agent (子任务代理)** - 执行具体的子任务
7. **Reflection (反思)** - 评估任务执行效果

## 详细流程

### 1. 初始用户输入和任务编排

1. **用户提供指令** → Interface
2. **Interface** → Task Stack: 发送用户消息
3. **Task Stack** 内部操作：
   - 检查用户消息
   - 检查当前任务栈和状态
4. **Director Agent** 执行：
   - 推理和规划 (Reasoning & Planning)
5. **Task Stack** 更新：
   - 更新任务栈
   - 获取下一个任务
   - 更新任务状态
6. **Director Agent** → **Assistant Agent**: "交给Assistant执行"

### 2. 任务执行阶段

1. **Assistant Agent** 内部操作：
   - 检查选定的代理需求
   - 从工作空间检索内容 (Content Retrieval from workspace)
2. **Assistant Agent** → **Subtask Agent**: 提供输入
3. **Subtask Agent** 执行：完成子任务
4. **Subtask Agent** → **Assistant Agent**: 返回结果
5. **Assistant Agent** 内部操作：
   - 存储结果和日志到工作空间

### 3. 任务运行总结和用户更新

1. **Assistant Agent** → **Director Agent**: 提供任务运行总结
2. **Task Stack** 更新：
   - 更新任务状态和用户消息

### 4. 评估和反思阶段

1. **Assistant Agent** 触发反思：
   - 检查反思代理需求
   - 从工作空间检索内容
2. **Assistant Agent** → **Reflection**: 提供输入
3. **Reflection** 执行：判断执行效果
4. **Reflection** → **Assistant Agent**: 返回反思结果
5. **Assistant Agent** 内部操作：
   - 存储结果和日志到工作空间

### 5. 反思总结和进一步编排

1. **Assistant Agent** → **Director Agent**: 提供反思总结
2. **Director Agent** 再次执行：
   - 推理和规划 (基于反思总结)
3. **Task Stack** 更新：
   - 更新任务栈、状态和用户消息

### 6. 持续的用户界面更新

1. **Interface** 持续轮询：
   - 轮询更新变化
2. **Interface** → **Task Stack**: 获取新用户消息（如果有）
3. **Task Stack** → **Interface**: 更新任务状态和用户消息
4. **Interface** → **Task Stack**: 获取新信息（如果有）
5. **Task Stack** → **Interface**: 更新任务栈、状态和用户消息
6. **Interface** 显示：将所有信息变化展示给用户

## 关键交互点

### Director Agent 的职责

- **推理和规划**: 根据用户消息、任务栈状态、执行结果和反思结果进行推理
- **任务编排**: 更新任务栈，获取下一个任务
- **任务委托**: 将任务交给 Assistant Agent 执行
- **结果处理**: 接收任务运行总结和反思总结，进行下一步规划

### Assistant Agent 的职责

- **任务执行**: 协调子任务代理完成具体任务
- **内容检索**: 从工作空间检索相关信息
- **结果存储**: 将执行结果和日志存储到工作空间
- **反思触发**: 触发反思阶段，评估执行效果

### Task Stack 的职责

- **消息管理**: 接收和管理用户消息
- **任务管理**: 管理任务队列和状态
- **执行指针**: 跟踪当前执行位置
- **状态更新**: 更新任务状态和用户消息

## 实现说明

Director Agent 通过 HTTP API 与后端（Task Stack 和 Assistant）交互：

- **Task Stack API**: 检查消息、获取任务栈、创建任务、更新状态等
- **Assistant API**: 执行代理、获取执行结果等

Director Agent 运行在独立的循环中，持续监控系统状态并执行编排逻辑。
