# Generation Module

图像、视频、音频生成模块，提供可扩展的生成器注册机制。

## 概述

Generation 模块提供了统一的接口用于图像、视频和音频生成，采用插件式的注册机制，类似于 Agent 系统。每个生成器都可以定义自己的输入参数（通过 `input_schema`），系统会自动验证和提取这些参数。

另外，generation 提供了可复用的媒体服务实现（按模态分目录）：

- `generation/image_generators/service.py`: `ImageService` / `MockImageService`
- `generation/video_generators/service.py`: `VideoService` / `MockVideoService`
- `generation/audio_generators/service.py`: `AudioService` / `MockAudioService`

对应注册表：

- `generation/image_generators/registry.py`
- `generation/video_generators/registry.py`
- `generation/audio_generators/registry.py`

示例聚合目录（便于统一查看示例）：

- `generation/example_generators/`

这三者共享 `generation/base_registry.py` 的通用发现与注册逻辑，
仅保留各模态自己的输入参数签名与 `generate()` 包装。

这些服务用于承载 provider 耦合的执行逻辑，便于 `agents/` 直接复用。

## 核心概念

### 1. 生成器基类

- **BaseImageGenerator**: 所有图像生成器的基类
- **BaseVideoGenerator**: 所有视频生成器的基类
- **BaseAudioGenerator**: 所有音频生成器的基类

针对 service 驱动实现，还提供了模态内复用基类（位于各自 `generators/` 目录）：

- `BaseServiceImageGenerator`
- `BaseServiceVideoGenerator`
- `BaseServiceAudioGenerator`

每个生成器必须：
1. 继承对应的基类
2. 实现 `get_metadata()` 方法，定义输入/输出模式
3. 实现 `generate()` 方法，执行实际的生成逻辑

### 2. 注册机制

生成器通过自动发现机制注册（扫描各模态目录下的 `generators/` 子目录）：
- 图像生成器：`generation/image_generators/generators/`
- 视频生成器：`generation/video_generators/generators/`
- 音频生成器：`generation/audio_generators/generators/`

每个生成器应该是一个独立的目录，包含 `generator.py` 或 `__init__.py` 文件。

### 3. 输入模式（input_schema）

`input_schema` 定义了生成器接受的所有参数：

```python
input_schema={
    "prompt": {
        "type": "string",
        "required": True,
        "description": "Text prompt"
    },
    "width": {
        "type": "integer",
        "required": False,
        "default": 1024,
        "description": "Image width"
    }
}
```

系统会自动：
- 验证参数类型
- 检查必需参数
- 应用默认值
- 提取参数传递给 `generate()` 方法

## 使用方法

### 1. 列出可用的生成器

```python
from inference import (
    get_image_generator_registry,
    get_video_generator_registry,
    get_audio_generator_registry,
)

# 图像生成器
image_registry = get_image_generator_registry()
generators = image_registry.list_generators()
print(generators)  # ['openrouter_image_generator', ...]

# 视频生成器
video_registry = get_video_generator_registry()
generators = video_registry.list_generators()
print(generators)  # ['mock_video_generator', ...]

# 音频生成器
audio_registry = get_audio_generator_registry()
generators = audio_registry.list_generators()
print(generators)  # ['openai_tts_generator', ...]
```

### 2. 生成图像

```python
from inference import get_image_generator_registry

registry = get_image_generator_registry()

# 使用文本提示生成图像
result = registry.generate(
    generator_id="openrouter_image_generator",
    prompt="A beautiful sunset"
)

print(result["images"])  # Base64 编码的图像列表
print(result["metadata"])  # 生成模式、字节数等元信息
```

### 3. 使用输入图像（图像到图像）

```python
result = registry.generate(
    generator_id="openrouter_image_generator",
    prompt="Transform this image",
    images=["path/to/input1.jpg", "path/to/input2.jpg"]
)
```

### 4. 生成视频

```python
from inference import get_video_generator_registry

registry = get_video_generator_registry()

# 文本到视频
result = registry.generate(
    generator_id="mock_video_generator",
    prompt="A cat walking",
    duration=5,
    fps=24
)

# 图像到视频
result = registry.generate(
    generator_id="mock_video_generator",
    prompt="Animate this image",
    images=["path/to/image.jpg"],
    duration=3
)

# 视频到视频
result = registry.generate(
    generator_id="mock_video_generator",
    prompt="Apply artistic style",
    videos=["path/to/video.mp4"],
    duration=5
)
```

### 5. 生成音频

```python
from inference import get_audio_generator_registry

registry = get_audio_generator_registry()

result = registry.generate(
    generator_id="openai_tts_generator",
    text="Hello from FrameWorkers",
    response_format="wav",
)
```

### 6. 获取生成器信息

```python
generator = registry.get_generator("openrouter_image_generator")

# 获取输入模式
input_schema = generator.get_input_schema()
print(input_schema)

# 获取输出模式
output_schema = generator.get_output_schema()
print(output_schema)

# 获取完整信息
info = generator.get_info()
print(info)
```

## 创建自定义生成器

### 步骤 1: 创建目录结构

```
generation/
└── image_generators/  # 或 video_generators/ / audio_generators/
    └── generators/
        └── my_generator/
            ├── __init__.py
            └── generator.py
```

### 步骤 2: 实现生成器类

参考 `generation/example_generators/example_generator.py`，创建你的生成器：

```python
from ....base_generator import BaseImageGenerator, GeneratorMetadata

class MyImageGenerator(BaseImageGenerator):
    def get_metadata(self) -> GeneratorMetadata:
        return GeneratorMetadata(
            id="my_image_generator",
            name="My Image Generator",
            description="My custom image generator",
            input_schema={
                "prompt": {
                    "type": "string",
                    "required": True,
                    "description": "Text prompt"
                },
                # 定义其他参数...
            },
            output_schema={
                "images": {
                    "type": "array",
                    "description": "Generated images"
                }
            }
        )
    
    def generate(self, **kwargs) -> Dict[str, Any]:
        # 提取参数
        prompt = kwargs.get("prompt")
        
        # 实现你的生成逻辑
        # - 调用 API（OpenAI DALL-E, Stability AI 等）
        # - 使用本地模型（Stable Diffusion 等）
        
        # 返回结果
        return {
            "images": [...],
            "image_paths": [...],
            "metadata": {...}
        }
```

### 步骤 3: 导出生成器

在 `__init__.py` 中：

```python
from .generator import MyImageGenerator

__all__ = ["MyImageGenerator"]
```

### 步骤 4: 自动注册

生成器会被自动发现和注册，无需额外配置。

## 输入模式规范

### 支持的类型

- `string`: 字符串
- `integer`: 整数
- `float`: 浮点数
- `boolean`: 布尔值
- `array`: 数组
- `object`: 对象

### 字段定义

```python
{
    "field_name": {
        "type": "string",           # 必需：字段类型
        "required": True,            # 可选：是否必需（默认 False）
        "default": "default_value",  # 可选：默认值
        "description": "..."        # 可选：字段描述
    }
}
```

## 输出模式规范

输出模式定义了生成器返回的数据结构：

```python
output_schema={
    "images": {
        "type": "array",
        "description": "List of generated images"
    },
    "metadata": {
        "type": "object",
        "description": "Additional metadata"
    }
}
```

## 示例生成器

模块包含统一示例生成器（`example_generators/example_generator.py`），展示了如何：
- 定义输入/输出模式
- 实现生成逻辑
- 处理不同类型的输入
- 返回标准化的结果

## 注意事项

1. **参数验证**: 系统会自动验证参数，但生成器内部也应该进行额外的验证
2. **错误处理**: `generate()` 方法应该抛出清晰的错误信息
3. **异步支持**: 对于长时间运行的生成任务，考虑实现异步版本
4. **资源管理**: 注意管理内存和文件资源
5. **API Keys**: 如果使用外部 API，确保安全地管理 API keys

## 扩展建议

- 添加进度回调支持
- 实现批量生成
- 添加生成历史记录
- 支持流式输出（对于视频）
- 添加生成队列管理
