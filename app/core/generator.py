from app.services.llm_service import LLMService
from app.core.faq_generator import generate_faq
from typing import Dict, Optional

llm_service = LLMService()

async def generate_readme(
    project_info: Dict,
    user_requirements: Optional[str] = None,
    platform: str = "github",
    model_name: Optional[str] = None,
    api_base: Optional[str] = None
) -> str:
    # 构建详细的 prompt
    prompt = f"""
你是一个专业的开源项目文档撰写专家。请根据以下项目信息，生成一个完整的 README.md 文件，要求结构清晰、内容专业、排版美观。必须包含以下章节（如果项目没有相关内容可以简要说明）：
- 项目名称（根据项目推测）
- 项目介绍
- 安装指南
- 快速开始（包含代码示例）
- API 文档（如果存在明显的 API 入口，否则生成简要说明）
- 贡献指南
- 许可证
- 常见问题（FAQ）

项目分析结果：
- 主要语言：{project_info.get('language')}
- 使用的框架：{project_info.get('framework')}
- 依赖库：{project_info.get('dependencies')}
- 入口文件：{project_info.get('entry_points')}
- 许可证类型：{project_info.get('license')}
- 是否包含示例代码：{project_info.get('has_examples')}

项目文件结构（可视化）：
{project_info.get('file_tree')}


关键代码片段（入口文件）：
{project_info.get('code_snippets')}

生成 FAQ 时，请参考以下内容：
FAQ 内容：
{await generate_faq(project_info, issues=None)}  # 实际可传入 issues

用户额外要求（如果有）：{user_requirements if user_requirements else "无"}

目标平台：{platform}（注意：如果是 Gitee，请避免使用 Gitee 不完全支持的 Markdown 语法，如任务列表嵌套、复杂表格等；如果是 GitHub 则无限制）

请直接输出 Markdown 文本，不要包含额外解释。
"""
    readme = await llm_service.generate_readme(prompt, model=model_name, api_base=api_base)
    return readme

async def generate_understanding(project_info: dict, model_name: str = None, api_base: str = None) -> str:
    """生成项目理解指南 UNDERSTANDING.md"""
    prompt = f"""
你是一位资深软件架构师和文档专家。请根据以下项目信息，生成一份详细的 **项目理解指南**，命名为 `UNDERSTANDING.md`。内容应面向想要深入理解该项目的新开发者，必须包含：

1. **整体架构** - 模块划分、依赖关系（可用 Mermaid 图）
2. **核心数据流** - 请求从入口到响应的完整路径
3. **关键类/函数** - 列出最重要的几个类/函数及其职责
4. **设计模式与决策** - 解释项目中使用的设计模式及关键设计取舍
5. **扩展点** - 如何扩展功能（例如添加新命令、新 API）
6. **常见修改场景** - 例如“如何修改配置文件”、“如何增加一个新的 API 接口”
7. **代码组织建议** - 推荐新手阅读文件的顺序

项目信息：
- 名称: {project_info.get('source_name', '未知')}
- 语言: {project_info.get('language')}
- 框架: {project_info.get('framework')}
- 入口文件: {project_info.get('entry_points')}
- 依赖: {project_info.get('dependencies')}
- 文件结构预览:
{project_info.get('file_tree_preview', '')}

关键代码片段：
{project_info.get('code_snippets', {})}

请直接输出 Markdown 格式的文档，不要包含额外解释。
"""
    generate_understanding_readme = await llm_service.generate_readme(prompt, model=model_name, api_base=api_base)
    return generate_understanding_readme