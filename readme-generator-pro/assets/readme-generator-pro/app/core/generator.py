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


# app/core/generator.py
async def generate_project_html(
        project_info: Dict,
        github_url: str = None,
        model_name: Optional[str] = None,
        api_base: Optional[str] = None
) -> str:
    """生成论文风格的项目介绍 HTML 页面，包含 Mermaid 图表和 GitHub 链接"""

    # 准备文件结构（JSON 字符串）
    file_tree_json = project_info.get("file_tree_json", {})
    import json
    file_tree_str = json.dumps(file_tree_json, indent=2, ensure_ascii=False)[:2000]

    # 构建详细的提示
    prompt = f"""
你是一位技术文档专家和前端设计师。请根据以下项目信息，生成一个完整的、可直接在浏览器中打开的 HTML 文档。
该文档应具有以下特点：
- 论文级别的排版，专业、清晰、精美，适合展示项目全貌。
- 包含以下章节：项目概述、核心架构、模块详解、安装与使用、API 参考、贡献指南、许可证。
- 必须包含至少 3 个 Mermaid 图表（例如：系统架构图、模块依赖图、数据流图或项目目录结构图）。
- 包含一个醒目的 GitHub 链接按钮，点击后跳转到指定的仓库地址（地址由外部提供：{github_url if github_url else "未提供，请先占位并提示用户设置"}）。
- 样式现代，支持明/暗色自适应（或提供优雅的浅色主题），使用 Flexbox/Grid 布局，代码块使用深色背景。
- 无需任何外部依赖（但允许使用 FontAwesome、Google Fonts 等 CDN，以及 Mermaid CDN）。
- 页面标题自动从项目名称生成。
- 内容真实，基于以下数据生成，不得编造不存在的功能。

项目分析结果：
- 项目名称/来源：{project_info.get('source_name', '未知项目')}
- 主要语言：{project_info.get('language')}
- 使用的框架：{project_info.get('framework')}
- 依赖库摘要：{project_info.get('dependencies')}
- 入口文件：{project_info.get('entry_points')}
- 许可证类型：{project_info.get('license')}
- 是否包含示例代码：{project_info.get('has_examples')}

文件结构（JSON 树）：
{file_tree_str}

关键代码片段（入口文件前 2000 字符）：
{project_info.get('code_snippets', {})}

文件内容片段（其他关键文件）：
{ {k: v[:800] for k, v in project_info.get('file_contents', {}).items() if k in project_info.get('entry_points', [])[:3]} }

请直接输出完整的 HTML 代码，确保 Mermaid 图表正确加载（在 <head> 中引入 Mermaid，并调用 mermaid.initialize）。不要包含任何解释文字。
"""
    # 调用 LLM，使用较大的 max_tokens
    html_content = await llm_service.generate_readme(
        prompt,
        model=model_name,
        api_base=api_base,
        max_tokens=8000  # 足够生成完整页面
    )
    # 确保返回的内容是完整的 HTML，如果模型可能输出多余标记，简单清理
    if not html_content.strip().startswith("<!DOCTYPE html>"):
        # 尝试从第一个 <html 或 <!DOCTYPE 开始截取
        import re
        match = re.search(r'(<!DOCTYPE html>.*|<\s*html.*)', html_content, re.DOTALL | re.IGNORECASE)
        if match:
            html_content = match.group(1)
    return html_content