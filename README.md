# 📄 README Generator Pro

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/LLM-API-412991)](https://platform.openai.com/)

**README Generator Pro** 是一款基于大语言模型（LLM）的智能 README 文档生成工具。只需提供 GitHub 仓库链接或上传工程文件夹，即可在数秒内自动生成结构完整、排版美观、内容专业的 `README.md` 文件。支持自然语言交互修改、多编程语言自适应、平台渲染优化（GitHub / Gitee）以及项目结构可视化分析。

> ⚠️ 注意：当前版本侧重于核心 README 生成与项目理解，Issues 自动生成 FAQ 功能尚在开发中，预计后续版本支持。

---

## ✨ 特性

- 🚀 **快速生成** – 从代码结构、依赖文件、入口函数智能生成标准 README 章节
- 🧠 **LLM 驱动** – 基于 OpenAI GPT / DeepSeek / 其他兼容 API 撰写文档内容
- 🔍 **基础项目分析** – 自动识别编程语言、主流框架、依赖摘要、入口文件、许可证类型
- 🌐 **多语言支持** – Python / JavaScript / TypeScript / Go / Rust / Java 等，LLM 会根据项目信息生成对应安装与运行命令
- 📝 **自然语言修改** – 生成后可通过对话动态调整章节顺序、增删内容
- 📁 **可视化文件树** – 自动输出项目结构，支持点击查看文件内容及功能注释
- ❓ **通用 FAQ 生成** – 根据项目语言和框架生成通用常见问题（后续计划集成 GitHub Issues）
- 🎨 **平台适配** – 针对 GitHub、Gitee 的 Markdown 渲染差异进行基础语法调整（任务列表、表格分隔符等）
- 💻 **友好交互界面** – 提供 Web UI 与 RESTful API 两种使用方式，支持 SSE 进度推送

---

## 🛠️ 安装指南

### 环境要求
- Python 3.10 或更高版本
- （可选）LLM API Key（OpenAI / DeepSeek 等） – 用于实际生成，若不配置则自动启用模拟模式（仅用于测试）

### 克隆仓库
```bash
git clone https://github.com/yourusername/readme-generator-pro.git
cd readme-generator-pro
```

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置环境变量
复制 `.env.example` 为 `.env`，并根据需要修改：
```ini
LLM_API_KEY=your_api_key_here           # 例如 OpenAI 或 DeepSeek 的 API Key，留空则启用 Mock 模式
LLM_API_BASE=https://api.openai.com/v1  # 自定义 API 端点，如 DeepSeek: https://api.deepseek.com/v1
LLM_MODEL=gpt-3.5-turbo                 # 使用的模型名称，如 deepseek-chat
GITHUB_TOKEN=optional_github_token      # 可选，用于访问私有仓库（暂未完全集成）
USE_MOCK_LLM=false                      # true 时无需 API Key，返回示例 README
```

> 💡 如果未设置 `LLM_API_KEY`，系统会自动进入 Mock 模式（`USE_MOCK_LLM=true`），无需付费即可体验流程。

---

## 🚀 快速开始

### 方式一：Web UI 界面
```bash
python run.py
```
浏览器访问 `http://localhost:8000`，即可看到图形界面：

1. 输入 GitHub 仓库链接（如 `https://github.com/user/repo`）**或** 上传本地工程文件夹（支持 ZIP 或直接选择文件夹）
2. （可选）填写额外要求，例如“强调性能测试结果”“添加 Docker 部署说明”
3. 选择目标平台（GitHub 或 Gitee）
4. 点击 **生成 README**，系统会先上传并分析项目，右侧将显示项目结构树和生成的文档
5. 如需修改，在下方的输入框中填写自然语言指令（如“删除 API 文档章节”），点击 **修改 README**

> 📁 **上传过滤说明**：为提升速度和节约资源，系统会自动跳过以下文件的内容（仅保留文件名占位）：  
> - 常见缓存目录（`__pycache__`、`node_modules`、`.venv` 等）  
> - 模型权重文件（`.bin`、`.pth`、`.safetensors`、`.onnx` 等）  
> - 超过 1MB 的大文件  
> - 非文本格式（如图片、视频）  
> 您无需手动清理，前端会智能过滤。

### 方式二：使用 REST API

#### 生成 README（通过 GitHub 链接）
```bash
curl -X POST http://localhost:8000/api/generate \
  -F "repo_url=https://github.com/facebook/react" \
  -F "user_requirements=包含性能测试数据" \
  -F "platform_target=github"
```

#### 生成 README（上传 ZIP 文件夹）
```bash
curl -X POST http://localhost:8000/api/generate \
  -F "folder_zip=@/path/to/your/project.zip" \
  -F "user_requirements=添加环境变量说明"
```

#### 修改已生成的 README（同步接口）
```bash
curl -X POST http://localhost:8000/api/modify \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "返回的会话ID",
    "modification": "把安装命令放在最前面",
    "platform_target": "github"
  }'
```

响应示例：
```json
{
  "session_id": "abc-123",
  "readme_content": "# 项目名称\n...",
  "file_tree_preview": "📁 project/\n  - main.py  # 主程序入口"
}
```

> 💡 对于大型项目，建议使用异步任务接口 `/api/generate-task` + SSE 进度查询（Web UI 已集成）。

---

## 📖 API 文档

### `POST /api/generate`
生成 README 文档（同步接口，适合中小项目）。

**请求参数**（`multipart/form-data`）：
| 参数名             | 类型   | 必填 | 描述                                                         |
| ------------------ | ------ | ---- | ------------------------------------------------------------ |
| `repo_url`         | string | 二选一 | GitHub 仓库链接                                              |
| `folder_zip`       | file   | 二选一 | 工程文件夹的 ZIP 压缩包                                      |
| `folder_files`     | file[] | 二选一 | 直接上传多个文件（前端使用 `webkitdirectory` 特性）          |
| `user_requirements`| string | 否   | 额外的内容要求，如“强调性能测试”                              |
| `platform_target`  | string | 否   | `github` 或 `gitee`，默认为 `github`                         |
| `model_name`       | string | 否   | 覆盖环境变量的模型名称，如 `deepseek-chat`                   |
| `api_base`         | string | 否   | 覆盖环境变量的 API 端点                                      |
| `ignored_files`    | string | 否   | JSON 数组，需要忽略的相对于根目录的文件路径列表（前端自动生成） |

**响应**：
```json
{
  "session_id": "uuid",
  "readme_content": "markdown文本",
  "file_tree_preview": "项目结构树（文本）",
  "file_tree_json": { ... }   // 结构化文件树对象
}
```

### `POST /api/modify`
基于已有会话修改 README（同步接口）。

**请求体**（`application/json`）：
| 参数名             | 类型   | 必填 | 描述                     |
| ------------------ | ------ | ---- | ------------------------ |
| `session_id`       | string | 是   | 上次生成返回的会话 ID     |
| `modification`     | string | 是   | 自然语言修改指令         |
| `platform_target`  | string | 否   | 目标平台，默认 `github`  |
| `model_name`       | string | 否   | 可选模型覆盖             |
| `api_base`         | string | 否   | 可选 API 端点覆盖        |

**响应**：同 `/api/generate`。

### 异步任务接口（推荐用于大项目）
- `POST /api/generate-task` – 提交生成任务，返回 `task_id`
- `GET /api/task/{task_id}/stream` – SSE 实时获取进度和结果
- Web UI 已完整集成，您也可以参考前端代码自行调用。

其他辅助接口：
- `POST /api/chat?session_id=xxx&question=...` – 项目问答助手
- `POST /api/understanding?session_id=xxx` – 生成 `UNDERSTANDING.md` 项目理解文档
- `GET /api/file_content?session_id=xxx&file_path=...` – 获取文件内容及功能注释

---

## 🤝 贡献指南

我们欢迎任何形式的贡献！请遵循以下流程：

1. **Fork 本仓库** 并克隆到本地
2. **创建新分支**：`git checkout -b feature/your-feature`
3. **提交代码**：确保代码风格符合 PEP8（Python）、使用 `black` 格式化
4. **编写测试**：针对新增功能添加单元测试（位于 `tests/` 目录）
5. **发起 Pull Request**：描述清楚改动内容和动机

### 开发环境搭建
```bash
# 安装开发依赖
pip install -r requirements-dev.txt   # 包含 pytest, black, flake8 等

# 运行测试
pytest tests/

# 代码格式化
black app/ run.py
```

### 报告 Bug 或建议
请在 [Issues](https://github.com/yourusername/readme-generator-pro/issues) 页面详细描述问题或新功能建议，并附上相关日志或示例。

---

## 📄 许可证

本项目使用 [MIT 许可证](LICENSE)。您可以自由使用、修改和分发，但需保留原始版权声明。

---

## ❓ 常见问题（FAQ）

### Q：没有 LLM API Key 可以正常使用吗？
**A**：可以。将环境变量 `USE_MOCK_LLM` 设置为 `true`（或不设置 `LLM_API_KEY`，系统自动启用），将使用内置模拟生成器输出示例 README。但推荐配置真实 API Key 以获得更精准、丰富的内容。

### Q：支持私有 GitHub 仓库吗？
**A**：当前版本暂未完全支持。您可以在 `.env` 中配置 `GITHUB_TOKEN`，但需要自行修改 `analyzer.analyze_github` 传递 token。后续版本会完善此功能。

### Q：为什么生成的 README 中某些章节是空的？
**A**：如果您的项目缺少某些典型文件（如 `LICENSE`、`examples/` 目录），Agent 会根据最佳实践生成一个通用占位符或建议。您可以通过修改指令补充内容。

### Q：如何让 Agent 扫描 Issues 生成 FAQ？
**A**：该功能计划在后续版本实现（基于 GitHub API 拉取 Issues）。目前系统会生成基于项目语言和框架的通用 FAQ。

### Q：生成的 README 中图片路径如何处理？
**A**：Agent 会自动检测项目中 `./docs/fig.png` 之类的相对路径，并根据目标平台在 Prompt 中建议合适写法。您也可以在上传文件夹前将图片放在 `docs/` 目录下。

### Q：能否批量生成多个仓库的 README？
**A**：可以。您可以使用脚本调用 API 接口，循环提交不同 `repo_url`，并保存返回的 `readme_content`。后续我们会提供 CLI 工具简化批量操作。

### Q：上传文件夹时，为什么有些文件没有被分析？
**A**：系统会自动跳过模型权重文件（`.bin`、`.pth`、`.safetensors` 等）、大于 1MB 的文件、以及常见临时目录（`__pycache__`、`node_modules` 等）。这些文件的内容不会被读取，但文件名仍会显示在文件树中（占位）。这样可以大幅提升上传速度并节约 API 成本。

### Q：如何自定义 LLM 端点（例如使用 DeepSeek、LocalAI）？
**A**：在 `.env` 中设置 `LLM_API_BASE` 和 `LLM_MODEL`。例如使用 DeepSeek：
```ini
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
LLM_API_KEY=your_deepseek_api_key
```
然后在 Web UI 或 API 请求中可进一步覆盖。

---

## 📞 联系与支持

- 项目作者：[Your Name](mailto:youremail@example.com)
- 项目地址：[https://github.com/yourusername/readme-generator-pro](https://github.com/yourusername/readme-generator-pro)
- 问题反馈：请提交 [GitHub Issues](https://github.com/yourusername/readme-generator-pro/issues)

---

**如果这个项目对您有帮助，请给一个 ⭐ Star 支持我们！**
```

### 主要改动说明：
1. **环境变量** – 统一为 `LLM_API_KEY`，与代码一致；补充了 `LLM_API_BASE` 和 `LLM_MODEL` 的说明。
2. **FAQ 功能** – 明确标注为“通用 FAQ”，Issues 集成标注为后续版本。
3. **过滤规则** – 新增上传过滤说明，解释为何部分文件未被分析。
4. **API 示例** – 修正 curl 中的 `folder` 为 `folder_zip`；补充异步任务说明。
5. **弱化承诺** – 将“深度项目分析”改为“基础项目分析”，强调 LLM 生成命令的不确定性。
6. **私有仓库** – 明确暂未完全支持。
7. **自定义模型** – 增加 DeepSeek 配置示例。
8. **其他细节** – 修正 OpenAI 链接，补充 SSE 进度说明，添加 Web UI 中修改操作的描述。