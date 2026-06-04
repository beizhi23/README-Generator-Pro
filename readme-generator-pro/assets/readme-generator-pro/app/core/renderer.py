import re

def adapt_markdown_for_platform(content: str, platform: str) -> str:
    """根据平台调整 Markdown 语法"""
    if platform == "gitee":
        # Gitee 不支持某些任务列表嵌套，简化任务列表语法
        content = re.sub(r'- \[ \]', '- [ ]', content)  # 确保空格格式
        # 移除多行表格（可选简单替换）
        # 如果存在复杂表格警告，我们仅作简单示例
        content = content.replace("| --- | --- |", "| - | - |")  # 示例简单处理
        # Gitee 图片相对路径可能需处理，这里留作扩展
    return content