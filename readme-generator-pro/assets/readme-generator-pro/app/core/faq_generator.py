from typing import List, Dict, Optional

async def generate_faq(project_info: Dict, issues: Optional[List[Dict]] = None) -> str:
    """从 issues 提取高频问题，否则基于复杂度生成通用 FAQ"""
    if issues and len(issues) > 0:
        # 简单取前5个 issue 的标题作为问题
        faq_items = []
        for issue in issues[:5]:
            title = issue.get("title", "")
            body = issue.get("body", "")[:200]
            faq_items.append(f"**Q: {title}**\n\n{body}\n")
        return "\n".join(faq_items)
    else:
        # 通用 FAQ 基于语言框架
        lang = project_info.get("language", "")
        framework = project_info.get("framework", "")
        return f"""
**Q: 如何安装依赖？**  
请参考上面的安装指南。

**Q: 支持哪些操作系统？**  
本项目主要使用 {lang} 开发，跨平台支持。

**Q: 如何贡献代码？**  
请阅读贡献指南（可后续补充）。
"""