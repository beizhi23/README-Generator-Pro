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
    """生成论文风格的项目介绍 HTML 页面（简洁学术风，无 Mermaid）"""

    # 准备文件结构（JSON 字符串）
    file_tree_json = project_info.get("file_tree_json", {})
    import json
    file_tree_str = json.dumps(file_tree_json, indent=2, ensure_ascii=False)[:2000]

    # 构建完整的提示
    prompt = f"""
你是一位顶级的学术项目网页设计师和前端工程师。请根据以下项目信息，生成一个以下风格的HTML页面。

## 页面核心设计规范（必须严格遵守）
1. **整体布局**：
   - 全页面居中对齐，最大宽度1200px，左右自动边距
   - 极简白色背景，黑色文字，无多余装饰
   - 所有内容垂直居中排列
   - 顶部有足够的内边距（padding-top: 80px）

2. **标题区域**：
   - 项目标题使用超大号粗体字体（font-size: 3.5rem）
   - 标题自动换行，居中显示
   - 标题下方有足够的间距（margin-bottom: 40px）

3. **作者区域**：
   - 作者列表使用中等大小字体（font-size: 1.5rem）
   - 作者名字之间用逗号分隔
   - 作者单位用上标数字标注（如¹, ², ³）
   - 通讯作者用*标注，项目负责人用†标注
   - 作者列表下方是单位列表，对应上标数字
   - 单位列表下方是通讯作者/项目负责人说明（灰色小字）

4. **按钮区域**：
   - 三个等宽的圆角黑色按钮（border-radius: 9999px）
   - 按钮内文字为白色，包含FontAwesome图标
   - 按钮之间有20px间距
   - 按钮悬停时有轻微的透明度变化
   - 按钮文字分别为：📄 Paper、💻 Code、🚀 Demo（根据项目实际情况调整）

5. **内容区域**：
   - 按钮下方是项目展示图片/视频区域
   - 图片宽度100%，圆角显示
   - 下方可添加项目概述、效果展示、引用等章节
   - 保持简洁的排版风格

## 必须包含的内容
- 项目完整标题（从项目名称自动生成）
- 作者列表（如果项目信息中没有，使用"Anonymous Authors"占位）
- 单位列表（如果没有，使用"Research Institution"占位）
- 三个核心按钮：Paper、Code、Demo（根据实际情况调整文字和链接）
- GitHub链接按钮（跳转到：{github_url if github_url else "#"}）
- 项目概述段落
- 至少1张项目效果展示图（使用占位图，提示用户替换）
- BibTeX引用格式

## 技术要求
- 使用Tailwind CSS CDN进行样式设计
- 使用FontAwesome CDN提供图标
- 无需任何外部JavaScript依赖
- 响应式设计，适配移动端
- 代码简洁高效，无冗余
- 直接输出完整的HTML代码，不要包含任何解释文字

## 项目分析信息
- 项目名称：{project_info.get('source_name', '未知项目')}
- 主要语言：{project_info.get('language')}
- 使用的框架：{project_info.get('framework')}
- 许可证类型：{project_info.get('license')}
- GitHub仓库：{github_url if github_url else "未提供"}
- 入口文件：{project_info.get('entry_points')}
- 依赖库：{project_info.get('dependencies')}
- 是否包含示例代码：{project_info.get('has_examples')}

## 项目文件结构
{file_tree_str}


## 关键代码片段（入口文件前2000字符）
{project_info.get('code_snippets', {})}

## 文件内容片段
{ {k: v[:800] for k, v in project_info.get('file_contents', {}).items() if k in project_info.get('entry_points', [])[:3]} }

请严格按照上述设计规范生成HTML代码。直接输出完整的HTML代码，不要包含任何解释文字。
"""
    # 调用 LLM
    html_content = await llm_service.generate_readme(
        prompt,
        model=model_name,
        api_base=api_base,
        max_tokens=8000
    )
    # 确保返回的内容是完整的 HTML
    if not html_content.strip().startswith("<!DOCTYPE html>"):
        import re
        match = re.search(r'(<!DOCTYPE html>.*|<\s*html.*)', html_content, re.DOTALL | re.IGNORECASE)
        if match:
            html_content = match.group(1)
    return html_content