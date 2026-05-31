import httpx
from typing import List, Dict, Optional
from app.core.utils import (
    IGNORE_DIRS, IGNORE_FILE_EXTS, TEXT_EXTS, MAX_FILE_SIZE_MB,
    is_path_ignored, should_ignore_file, is_text_file
)

async def fetch_repo_tree(owner: str, repo: str, token: Optional[str] = None) -> Dict:
    """
    获取仓库文件树（递归），并过滤无用文件/目录
    返回格式：{"files": [...], "contents": {...}}
    """
    # 尝试获取默认分支（main / master）
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Authorization": f"token {token}"} if token else {}
    async with httpx.AsyncClient() as client:
        # 获取仓库信息，确定默认分支
        repo_resp = await client.get(repo_url, headers=headers)
        repo_resp.raise_for_status()
        default_branch = repo_resp.json().get("default_branch", "main")

        # 获取文件树
        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
        tree_resp = await client.get(tree_url, headers=headers)
        tree_resp.raise_for_status()
        data = tree_resp.json()

        files = []
        contents = {}

        for item in data.get("tree", []):
            if item["type"] != "blob":
                continue  # 只处理文件

            path = item["path"]
            size = item.get("size", 0)

            # 1. 检查路径中是否包含被忽略的目录
            if is_path_ignored(path):
                continue

            # 2. 检查文件扩展名或大小是否应忽略
            if should_ignore_file(path, size):
                continue

            # 3. 记录文件基本信息
            files.append({"path": path, "size": size})

            # 4. 仅当是文本文件时，尝试获取内容（限制数量和大小）
            if is_text_file(path) and size < MAX_FILE_SIZE_MB * 1024 * 1024:
                # 限制最多获取 30 个文件的内容（避免 API 过载）
                if len(contents) < 30:
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{path}"
                    try:
                        content_resp = await client.get(raw_url, headers=headers)
                        if content_resp.status_code == 200:
                            contents[path] = content_resp.text[:2000]  # 截断
                    except Exception:
                        pass

        return {"files": files, "contents": contents}

async def fetch_repo_issues(owner: str, repo: str, token: Optional[str] = None) -> List[Dict]:
    """获取仓库 issues，用于 FAQ 生成"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=30"
    headers = {"Authorization": f"token {token}"} if token else {}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 200:
            issues = resp.json()
            # 过滤掉 pull requests
            return [i for i in issues if "pull_request" not in i]
        return []