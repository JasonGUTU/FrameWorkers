# Inference Module

Inference 模块提供了完整的语言模型推理、Prompt 处理和多模态支持工具。该模块设计为独立模块，可在需要时被其他模块调用。

## 功能特性

- **通用模型调用接口**: 使用 LiteLLM 包装，提供统一的 OpenAI 兼容接口调用所有支持的模型
- **自研模型接口**: 预留自定义模型接口，支持通过 LiteLLM 对接 Ollama 等本地模型
- **多模态支持**: 提供图像 Base64 编码/解码及相关工具
- **Prompt 处理工具**: Message 压缩、历史持久化等功能
- **Prompt 模板系统**: Prompt 组合与模板管理
- **图像生成模块**: 可扩展的图像生成器注册系统，支持文本到图像、图像到图像
- **视频生成模块**: 可扩展的视频生成器注册系统，支持文本/图像/视频到视频

## 目录结构

```
Inference/
├── __init__.py                 # 模块入口
├── README.md                   # 本文档
├── MODELS.md                   # 支持的模型清单
├── requirements.txt            # 依赖包
├── config/                     # 配置模块
│   ├── __init__.py
│   ├── model_config.py         # 模型配置和注册表
│   └── inference_config.yaml.example  # 配置文件示例
├── core/                       # 核心推理模块
│   ├── __init__.py
│   ├── llm_client.py           # LiteLLM 通用接口
│   └── custom_model.py         # 自研模型接口
├── multimodal/                 # 多模态支持
│   ├── __init__.py
│   ├── image_utils.py          # 图像工具（Base64 编码解码）
│   └── multimodal_utils.py     # 多模态通用工具
├── prompt/                     # Prompt 处理模块
│   ├── __init__.py
│   ├── message_utils.py        # Message 压缩等工具
│   ├── history.py              # 历史 Message 持久化
│   └── templates.py             # Prompt 模板和组合
├── generation/                 # 生成模块
│   ├── __init__.py
│   ├── base_generator.py        # 生成器基类
│   ├── image_generator_registry.py  # 图像生成器注册表
│   ├── video_generator_registry.py  # 视频生成器注册表
│   ├── image_generators/        # 图像生成器目录
│   │   └── example_generator/   # 示例图像生成器
│   ├── video_generators/        # 视频生成器目录
│   │   └── example_generator/   # 示例视频生成器
│   └── README.md                # 生成模块文档
└── utils/                      # 工具模块
    ├── __init__.py
    └── config_loader.py        # 配置加载工具
```

## 安装

### 1. 安装依赖

```bash
cd Inference
pip install -r requirements.txt
```

### 2. 配置 API Keys

复制配置文件示例并填写你的 API Keys:

```bash
cp config/inference_config.yaml.example config/inference_config.yaml
```

编辑 `config/inference_config.yaml`，填入你的 API Keys。你也可以使用环境变量：

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

## 快速开始

### 1. 基本模型调用

```python
from Inference import LLMClient, Message

# 初始化客户端（使用默认模型）
client = LLMClient(default_model="gpt-3.5-turbo")

# 或者从配置文件加载
client = LLMClient(config_path="config/inference_config.yaml")

# 调用模型
response = client.call(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(response["choices"][0]["message"]["content"])
```

### 2. 指定模型和参数

```python
from Inference import LLMClient, ModelConfig

client = LLMClient()

# 方式1: 通过参数指定模型
response = client.call(
    messages=[{"role": "user", "content": "Hello!"}],
    model="gpt-4o"
)

# 方式2: 使用 ModelConfig
config = ModelConfig(
    model="gpt-4o",
    temperature=0.9,
    max_tokens=2000,
    top_p=0.95
)

response = client.call(
    messages=[{"role": "user", "content": "Hello!"}],
    config=config
)
```

### 3. 流式调用

```python
# 同步流式调用
for chunk in client.stream_call(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="gpt-3.5-turbo"
):
    if chunk.get("choices"):
        delta = chunk["choices"][0].get("delta", {})
        content = delta.get("content", "")
        if content:
            print(content, end="", flush=True)

# 异步流式调用
import asyncio

async def stream_async():
    async for chunk in client.astream_call(
        messages=[{"role": "user", "content": "Tell me a story"}],
        model="gpt-3.5-turbo"
    ):
        if chunk.get("choices"):
            delta = chunk["choices"][0].get("delta", {})
            content = delta.get("content", "")
            if content:
                print(content, end="", flush=True)

asyncio.run(stream_async())
```

## 核心功能

### 1. 通用模型调用接口

`LLMClient` 提供了统一的接口，可以通过 OpenAI 兼容的方式调用所有支持的模型：

```python
from Inference import LLMClient

client = LLMClient()

# 调用 OpenAI 模型
response = client.call(
    messages=[{"role": "user", "content": "Hello!"}],
    model="gpt-4o"
)

# 调用 Anthropic 模型
response = client.call(
    messages=[{"role": "user", "content": "Hello!"}],
    model="claude-3-5-sonnet-20241022"
)

# 调用 Google 模型
response = client.call(
    messages=[{"role": "user", "content": "Hello!"}],
    model="gemini-pro"
)
```

### 2. 自研模型接口（Ollama）

支持通过 LiteLLM 或直接 API 调用 Ollama 模型：

```python
from Inference import CustomModelClient

# 初始化 Ollama 客户端
client = CustomModelClient(
    base_url="http://localhost:11434",
    default_model="llama3"
)

# 通过 LiteLLM 调用（推荐）
response = client.call(
    messages=[{"role": "user", "content": "Hello!"}],
    model="ollama/llama3"
)

# 或直接调用 Ollama API
response = client.call_ollama(
    messages=[{"role": "user", "content": "Hello!"}],
    model="llama3"
)

# 列出可用的 Ollama 模型
models = client.list_ollama_models()
print(models)

# 拉取新模型
client.pull_ollama_model("mistral")
```

注册自定义模型：

```python
client.register_custom_model(
    model_id="my-custom-model",
    name="My Custom Model",
    provider="custom",
    supports_streaming=True,
    supports_multimodal=False,
    max_tokens=4096,
    context_window=8192,
    description="My custom trained model"
)
```

### 3. 多模态支持

#### 图像编码解码

```python
from Inference import ImageUtils

# 将图像编码为 Base64
image_base64 = ImageUtils.encode_image_to_base64("path/to/image.png")
print(image_base64)  # data:image/png;base64,...

# 从 Base64 解码图像
image = ImageUtils.decode_base64_to_image(image_base64)

# 保存 Base64 图像到文件
ImageUtils.save_base64_image(image_base64, "output.png")

# 调整图像大小
resized = ImageUtils.resize_image("path/to/image.jpg", max_size=(1024, 1024))

# 获取图像信息
info = ImageUtils.get_image_info("path/to/image.png")
print(info)  # {'width': 1920, 'height': 1080, 'format': 'PNG', ...}
```

#### 创建多模态消息

```python
from Inference import ImageUtils, LLMClient

client = LLMClient()

# 创建包含图像的消息
multimodal_message = ImageUtils.create_multimodal_message(
    text="What's in this image?",
    image_path="path/to/image.png"
)

response = client.call(
    messages=[multimodal_message],
    model="gpt-4o"  # 需要支持多模态的模型
)
```

#### 多模态工具

```python
from Inference import MultimodalUtils

# 准备多模态内容
content = MultimodalUtils.prepare_multimodal_content(
    text="Analyze these images",
    images=["image1.png", "image2.jpg"]
)

# 从消息中提取图像
message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Look at this"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
    ]
}
images = MultimodalUtils.extract_images_from_message(message)

# 提取文本
text = MultimodalUtils.extract_text_from_message(message)

# 验证多模态消息格式
is_valid = MultimodalUtils.validate_multimodal_message(message)

# 估算 token 数量
tokens = MultimodalUtils.count_tokens_multimodal(message)
```

### 4. Prompt 处理工具

#### Message 压缩

```python
from Inference import MessageUtils

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Message 1"},
    {"role": "assistant", "content": "Response 1"},
    {"role": "user", "content": "Message 2"},
    {"role": "assistant", "content": "Response 2"},
]

# 压缩消息（移除最旧的消息）
compressed = MessageUtils.compress_messages(
    messages,
    max_tokens=1000,
    strategy="truncate_oldest"
)

# 合并相同角色的连续消息
merged = MessageUtils.merge_consecutive_same_role(messages)

# 估算 token 数量
tokens = MessageUtils.estimate_tokens(messages)
```

#### 历史 Message 持久化

```python
from Inference import MessageHistory

# 初始化历史记录（自动保存到文件）
history = MessageHistory(
    storage_path="./data/conversation_history.json",
    max_messages=100  # 最多保存 100 条消息
)

# 添加消息
history.add_message(
    role="user",
    content="Hello!"
)

history.add_message(
    role="assistant",
    content="Hi! How can I help you?"
)

# 获取消息（用于 API 调用）
messages = history.get_formatted_messages(for_api=True)

# 获取特定角色的消息
user_messages = history.get_messages(role="user")

# 获取统计信息
stats = history.get_statistics()
print(stats)  # {'total_messages': 2, 'role_counts': {...}, ...}

# 导出历史记录
history.export("./backup.json")

# 清空历史记录
history.clear()
```

### 5. Prompt 模板和组合

#### 创建和使用模板

```python
from Inference import PromptTemplate, TemplateManager

# 创建模板管理器
manager = TemplateManager(storage_path="./data/templates")

# 创建模板
template = manager.create_template(
    name="greeting",
    template="Hello, {name}! Welcome to {place}.",
    description="Greeting template",
    variables=["name", "place"]
)

# 格式化模板
prompt = manager.format_template(
    "greeting",
    name="Alice",
    place="Wonderland"
)
print(prompt)  # "Hello, Alice! Welcome to Wonderland."

# 或者直接使用 PromptTemplate
template = PromptTemplate(
    template="You are a {role}. Your task is to {task}.",
    name="system_prompt"
)

formatted = template.format(role="assistant", task="help users")
```

#### 组合多个模板

```python
# 组合多个模板
composed = manager.compose(
    templates=["system_prompt", "user_query"],
    separator="\n\n",
    role="assistant",
    task="answer questions",
    query="What is Python?"
)

# 组合成消息列表
messages = manager.compose_messages(
    templates=[
        {"role": "system", "template": "system_prompt"},
        {"role": "user", "template": "user_query"}
    ],
    role="assistant",
    task="help users",
    query="Hello!"
)
```

#### 模板管理

```python
# 列出所有模板
templates = manager.list_templates()

# 获取模板
template = manager.get_template("greeting")

# 验证模板变量
is_valid, missing = template.validate(name="Alice", place="Wonderland")

# 导出模板
manager.export_template("greeting", "./greeting_template.json")

# 导入模板
manager.import_template("./greeting_template.json")

# 删除模板
manager.remove_template("greeting")
```

## 配置

### 配置文件方式

创建 `config/inference_config.yaml`:

```yaml
# 默认模型
default_model: "gpt-3.5-turbo"

# API Keys（支持环境变量）
api_keys:
  openai: "${OPENAI_API_KEY}"
  anthropic: "${ANTHROPIC_API_KEY}"

# 自定义端点
custom_endpoints:
  ollama:
    base_url: "http://localhost:11434"

# 模型特定配置
model_configs:
  gpt-4:
    temperature: 0.7
    max_tokens: 4096
```

使用配置：

```python
client = LLMClient(config_path="config/inference_config.yaml")
```

### 环境变量方式

```bash
export INFERENCE_DEFAULT_MODEL="gpt-4o"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export OLLAMA_BASE_URL="http://localhost:11434"
```

### 代码方式

```python
from Inference import LLMClient, ModelConfig

client = LLMClient(default_model="gpt-4o")

config = ModelConfig(
    temperature=0.9,
    max_tokens=2000,
    api_key="your-api-key",
    base_url="https://api.openai.com/v1"
)

response = client.call(messages=[...], config=config)
```

## 模型清单

支持的模型列表请参考 [MODELS.md](./MODELS.md)。

### 查询可用模型

```python
from Inference import ModelRegistry, get_model_config

registry = ModelRegistry()

# 列出所有模型
all_models = registry.list_models()

# 按提供商列出
by_provider = registry.list_models_by_provider()

# 获取模型信息
model_info = get_model_config("gpt-4o")
print(model_info.name)
print(model_info.supports_multimodal)
print(model_info.max_tokens)
```

## 完整示例

### 示例 1: 带历史记录的对话

```python
from Inference import LLMClient, MessageHistory

client = LLMClient(default_model="gpt-3.5-turbo")
history = MessageHistory(storage_path="./conversation.json")

# 添加系统消息
history.add_message(role="system", content="You are a helpful assistant.")

# 用户消息
history.add_message(role="user", content="What is Python?")

# 调用模型
response = client.call(messages=history.get_formatted_messages())

# 保存助手回复
assistant_reply = response["choices"][0]["message"]["content"]
history.add_message(role="assistant", content=assistant_reply)

print(assistant_reply)
```

### 示例 2: 多模态图像分析

```python
from Inference import LLMClient, ImageUtils

client = LLMClient(default_model="gpt-4o")

# 创建多模态消息
message = ImageUtils.create_multimodal_message(
    text="What objects are in this image? Describe them in detail.",
    image_path="photo.jpg"
)

# 调用模型
response = client.call(messages=[message])
print(response["choices"][0]["message"]["content"])
```

### 示例 3: 使用模板的批量处理

```python
from Inference import LLMClient, TemplateManager

client = LLMClient()
manager = TemplateManager()

# 创建模板
manager.create_template(
    name="analysis",
    template="Analyze the following text and provide key insights:\n\n{text}"
)

# 批量处理
texts = ["Text 1", "Text 2", "Text 3"]
for text in texts:
    prompt = manager.format_template("analysis", text=text)
    response = client.call(messages=[{"role": "user", "content": prompt}])
    print(response["choices"][0]["message"]["content"])
```

### 示例 4: 流式响应处理

```python
from Inference import LLMClient

client = LLMClient()

def handle_stream(response_text):
    """处理流式响应"""
    print(response_text, end="", flush=True)

# 流式调用
full_response = ""
for chunk in client.stream_call(
    messages=[{"role": "user", "content": "Write a short story"}],
    model="gpt-3.5-turbo"
):
    if chunk.get("choices"):
        delta = chunk["choices"][0].get("delta", {})
        content = delta.get("content", "")
        if content:
            full_response += content
            handle_stream(content)

print(f"\n\nFull response length: {len(full_response)}")
```

### 示例 5: 图像生成

```python
from Inference import get_image_generator_registry

registry = get_image_generator_registry()

# 列出可用的生成器
generators = registry.list_generators()
print(f"Available generators: {generators}")

# 生成图像
result = registry.generate(
    generator_id="example_image_generator",
    prompt="A beautiful sunset over the ocean",
    width=1024,
    height=1024,
    style="realistic"
)

print(f"Generated {len(result['images'])} image(s)")
print(f"Saved to: {result['image_paths']}")
```

### 示例 6: 视频生成

```python
from Inference import get_video_generator_registry

registry = get_video_generator_registry()

# 文本到视频
result = registry.generate(
    generator_id="example_video_generator",
    prompt="A cat walking on the beach",
    duration=5,
    fps=24
)

print(f"Generated video: {result['video_path']}")

# 图像到视频
result = registry.generate(
    generator_id="example_video_generator",
    prompt="Animate this image",
    images=["path/to/image.jpg"],
    duration=3
)
```

## API 参考

### LLMClient

主要的语言模型客户端类。

**方法**:
- `call()`: 同步调用模型
- `acall()`: 异步调用模型
- `stream_call()`: 同步流式调用
- `astream_call()`: 异步流式调用
- `get_available_models()`: 获取可用模型列表
- `get_model_info()`: 获取模型信息

### CustomModelClient

自定义模型客户端，继承自 `LLMClient`。

**额外方法**:
- `register_custom_model()`: 注册自定义模型
- `call_ollama()`: 直接调用 Ollama API
- `stream_ollama()`: 流式调用 Ollama
- `list_ollama_models()`: 列出 Ollama 模型
- `pull_ollama_model()`: 拉取 Ollama 模型

### ImageUtils

图像处理工具类。

**方法**:
- `encode_image_to_base64()`: 编码图像为 Base64
- `decode_base64_to_image()`: 解码 Base64 为图像
- `save_base64_image()`: 保存 Base64 图像
- `resize_image()`: 调整图像大小
- `get_image_info()`: 获取图像信息
- `create_multimodal_message()`: 创建多模态消息

### MessageUtils

消息处理工具类。

**方法**:
- `compress_messages()`: 压缩消息
- `merge_consecutive_same_role()`: 合并相同角色的消息
- `truncate_messages()`: 截断消息
- `estimate_tokens()`: 估算 token 数量
- `extract_system_messages()`: 提取系统消息
- `get_message_count_by_role()`: 按角色统计消息

### MessageHistory

消息历史管理类。

**方法**:
- `add_message()`: 添加消息
- `add_messages()`: 批量添加消息
- `get_messages()`: 获取消息
- `get_formatted_messages()`: 获取格式化消息（用于 API）
- `clear()`: 清空历史
- `save()`: 保存历史
- `load()`: 加载历史
- `export()`: 导出历史
- `get_statistics()`: 获取统计信息

### TemplateManager

模板管理器类。

**方法**:
- `create_template()`: 创建模板
- `register_template()`: 注册模板
- `get_template()`: 获取模板
- `format_template()`: 格式化模板
- `compose()`: 组合模板
- `compose_messages()`: 组合为消息列表
- `list_templates()`: 列出模板
- `remove_template()`: 删除模板
- `save()`: 保存模板
- `load()`: 加载模板

### ImageGeneratorRegistry

图像生成器注册表。

**方法**:
- `list_generators()`: 列出所有注册的生成器 ID
- `get_generator()`: 获取生成器实例
- `generate()`: 使用指定生成器生成图像
- `get_all_generators_info()`: 获取所有生成器信息
- `register_generator()`: 手动注册生成器
- `reload()`: 重新加载所有生成器

### VideoGeneratorRegistry

视频生成器注册表。

**方法**:
- `list_generators()`: 列出所有注册的生成器 ID
- `get_generator()`: 获取生成器实例
- `generate()`: 使用指定生成器生成视频（支持文本/图像/视频输入）
- `get_all_generators_info()`: 获取所有生成器信息
- `register_generator()`: 手动注册生成器
- `reload()`: 重新加载所有生成器

### BaseImageGenerator / BaseVideoGenerator

生成器基类，所有自定义生成器必须继承这些类。

**方法**:
- `get_metadata()`: 返回生成器元数据（包括 input_schema 和 output_schema）
- `generate()`: 执行生成逻辑
- `validate_inputs()`: 验证输入参数
- `get_input_schema()`: 获取输入模式
- `get_output_schema()`: 获取输出模式
- `get_info()`: 获取生成器完整信息

## 注意事项

1. **API Keys**: 确保正确配置 API Keys，可以通过环境变量或配置文件设置
2. **模型可用性**: 某些模型可能需要特定的 API 访问权限
3. **Token 限制**: 注意模型的 token 限制，使用 `MessageUtils.estimate_tokens()` 进行估算
4. **多模态支持**: 只有部分模型支持多模态输入，请参考 [MODELS.md](./MODELS.md)
5. **Ollama**: 使用 Ollama 模型需要本地运行 Ollama 服务器
6. **异步调用**: 异步方法需要使用 `await` 关键字

## 故障排除

### LiteLLM 导入错误

如果遇到 `LiteLLM is not installed` 错误，请安装依赖：

```bash
pip install litellm
```

### Ollama 连接错误

确保 Ollama 服务正在运行：

```bash
# 检查 Ollama 状态
curl http://localhost:11434/api/tags

# 启动 Ollama（如果未运行）
ollama serve
```

### API Key 错误

检查环境变量或配置文件中的 API Keys 是否正确设置。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[添加许可证信息]
