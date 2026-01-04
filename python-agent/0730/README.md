# PDF to Markdown Conversion Tool

一个基于LLM的PDF转Markdown工具，支持并发处理和重试机制。

## 功能特性

### 🚀 核心功能
- **PDF转图片**：将PDF文件转换为高质量图片
- **并发处理**：使用线程池并发处理多张图片
- **LLM转换**：调用视觉语言模型将图片转换为Markdown
- **重试机制**：自动重试失败的请求（默认3次）
- **结果合并**：将多页结果合并为完整的Markdown文档

### 🛠️ 技术特性
- **线程池并发**：支持可配置的并发worker数量
- **错误处理**：完善的异常处理和错误恢复
- **进度监控**：实时显示处理进度和统计信息
- **灵活配置**：支持自定义模型、API密钥、重试次数等

## 安装依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv add PyMuPDF requests pillow pytest agno
```

## 快速开始

### 基本使用

```python
from utils.llm_pdf2md_tool import LLMPdf2MarkdownTool

# 初始化工具
tool = LLMPdf2MarkdownTool(
    model_id="qwen-vl-plus",
    max_workers=5,
    max_retries=3
)

# 转换PDF
result = tool.convert_pdf_to_markdown("sample/test_pdf01.pdf")

if result['success']:
    print(f"转换成功！处理了 {result['total_pages']} 页")
    print(f"成功页面: {result['successful_pages']}")
    print(f"失败页面: {result['failed_pages']}")
    print(f"处理时间: {result['processing_time_seconds']:.2f} 秒")
    
    # 保存结果
    with open("output.md", "w", encoding="utf-8") as f:
        f.write(result['combined_markdown'])
else:
    print(f"转换失败: {result['error']}")
```

### 高级配置

```python
# 自定义配置
tool = LLMPdf2MarkdownTool(
    model_id="qwen-vl-plus",
    api_key="your_api_key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.3,
    max_workers=10,
    max_retries=3,
    base_storage_path="custom_storage"
)

# 自定义提示词
custom_prompt = """
请仔细分析图片中的内容，并以结构化的markdown格式输出：
1. 识别标题和子标题
2. 提取列表和表格
3. 保持原始格式和结构
4. 如果有代码块，请用代码块格式
"""

# 转换指定页面范围
result = tool.convert_pdf_to_markdown(
    pdf_path="sample/test_pdf01.pdf",
    start_page=1,
    end_page=5,
    prompt=custom_prompt
)
```

### URL转换

```python
# 从URL转换PDF
result = tool.convert_pdf_url_to_markdown(
    pdf_url="https://example.com/document.pdf",
    start_page=1,
    end_page=10
)
```

## 测试

### 运行单元测试

```bash
# 运行所有测试
python -m pytest test_llm_pdf2md_tool.py -v

# 运行特定测试
python -m pytest test_llm_pdf2md_tool.py::TestLLMPdf2MarkdownTool::test_initialization -v
```

### 运行集成测试

```bash
# 需要设置API密钥
export DASHSCOPE_API_KEY="your_api_key"
python -m pytest test_llm_pdf2md_tool.py::TestIntegration::test_real_pdf_conversion -s -v
```

### 运行示例

```bash
# 运行基本测试
python test_pdf2md.py

# 运行使用示例
python example_usage.py
```

## 性能测试结果

从示例运行中可以看到不同worker数量的性能表现：

| Worker数量 | 处理时间 | 效率提升 |
|-----------|---------|---------|
| 1 worker  | 14.43秒 | 基准    |
| 3 workers | 10.31秒 | 28.5%   |
| 5 workers | 11.25秒 | 22.0%   |

## 文件结构

```
0730/
├── utils/
│   ├── llm_pdf2md_tool.py      # 主要工具类
│   ├── pdf2image_tool.py        # PDF转图片工具
│   └── file_downloader_tool.py  # 文件下载工具
├── storage/sample/
│   ├── test_pdf01.pdf          # 测试PDF文件
│   ├── output_basic.md         # 基本转换结果
│   └── output_custom_prompt.md # 自定义提示词结果
├── test_pdf2md.py              # 基本测试
├── test_llm_pdf2md_tool.py     # 单元测试
├── example_usage.py             # 使用示例
└── README.md                    # 说明文档
```

## 配置说明

### 环境变量

```bash
# 设置API密钥
export DASHSCOPE_API_KEY="your_api_key"
```

### 工具参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model_id` | str | "qwen-vl-plus" | LLM模型ID |
| `api_key` | str | None | API密钥 |
| `base_url` | str | DashScope URL | API基础URL |
| `temperature` | float | 0.3 | 生成温度 |
| `max_workers` | int | 10 | 最大并发worker数 |
| `max_retries` | int | 3 | 最大重试次数 |
| `base_storage_path` | str | None | 存储路径 |

## 错误处理

工具包含完善的错误处理机制：

1. **文件不存在**：自动检测并报告错误
2. **API调用失败**：自动重试（最多3次）
3. **图片处理失败**：记录错误但继续处理其他页面
4. **网络问题**：重试机制处理临时网络问题

## 输出格式

转换结果包含以下信息：

```python
{
    'success': True,
    'pdf_path': 'storage/sample/test_pdf01.pdf',
    'total_pages': 16,
    'processed_pages': 16,
    'processing_time_seconds': 90.24,
    'results': [...],  # 每页的详细结果
    'combined_markdown': '...',  # 合并的Markdown内容
    'successful_pages': 16,
    'failed_pages': 0
}
```

## 注意事项

1. **API密钥**：需要有效的DashScope API密钥
2. **网络连接**：需要稳定的网络连接访问API
3. **文件权限**：确保有读写权限
4. **内存使用**：大PDF文件可能占用较多内存
5. **处理时间**：取决于PDF页数和网络速度

## 许可证

MIT License 