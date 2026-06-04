import os
import re
from typing import Dict, List, Any, Optional, Tuple
from app.services.github_service import fetch_repo_tree
from app.core.utils import (
    detect_programming_language, detect_framework, parse_dependencies,
    generate_file_tree, identify_entry_points, extract_license_type,build_file_tree_json,
    should_ignore_dir, should_ignore_file, is_text_file
)

class ProjectAnalyzer:
    def __init__(self):
        self.project_data = {}

    async def analyze_github(self, repo_url: str, github_token: Optional[str] = None) -> Dict:
        """分析 GitHub 仓库"""
        # 解析 owner/repo
        pattern = r"github\.com/([^/]+)/([^/]+)"
        match = re.search(pattern, repo_url)
        if not match:
            raise ValueError("Invalid GitHub URL")
        owner, repo = match.groups()
        tree_data = await fetch_repo_tree(owner, repo, github_token)
        files = tree_data["files"]
        contents = tree_data["contents"]
        return self._analyze_files(files, contents, repo_url)

    def analyze_folder(self, folder_path: str, ignored_paths: List[str] = None) -> Dict:
        """分析本地文件夹，ignored_paths 是前端过滤后不上传内容的文件路径列表"""
        files = []
        contents = {}
        ignored_set = set(ignored_paths or [])

        for root, dirs, filenames in os.walk(folder_path):
            # 原有过滤（基于后端规则）仍然保留，防止漏网之鱼
            dirs[:] = [d for d in dirs if not should_ignore_dir(d)]
            for filename in filenames:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, folder_path)
                file_size = os.path.getsize(full_path)

                # 如果该文件在忽略列表中，只记录路径，不读取内容
                if rel_path in ignored_set:
                    files.append({"path": rel_path, "size": 0})  # 大小为0表示空壳
                    continue

                # 原有的后端过滤
                if should_ignore_file(filename, file_size):
                    continue

                files.append({"path": rel_path, "size": file_size})
                if is_text_file(filename):
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            contents[rel_path] = f.read(2000)
                    except Exception:
                        pass
        return self._analyze_files(files, contents, folder_path)

    def _analyze_files(self, files: List[Dict], contents: Dict, source_name: str) -> Dict:
        """通用分析逻辑"""
        file_paths = [f["path"] for f in files]
        # 依赖文件
        dep_files = [p for p in file_paths if p in ('requirements.txt', 'package.json', 'go.mod', 'Cargo.toml', 'pom.xml')]
        dependencies = {}
        for dep_file in dep_files:
            if dep_file in contents:
                dependencies.update(parse_dependencies(dep_file, contents[dep_file]))
        # 识别语言、框架
        lang = detect_programming_language(file_paths)
        framework = detect_framework(file_paths, contents)
        # 入口文件
        entry_points = identify_entry_points(file_paths)
        # 许可证
        license_file = next((p for p in file_paths if 'LICENSE' in p.upper()), None)
        license_type = extract_license_type(license_file, contents.get(license_file, '')) if license_file else "未指定"
        # 生成可视化树
        tree_str = generate_file_tree(file_paths, {p: "关键文件" for p in entry_points})
        # 代码片段（入口文件内容）
        code_snippets = {ep: contents.get(ep, "")[:1500] for ep in entry_points if ep in contents}

        file_contents = {}
        for path, content in contents.items():
            file_contents[path] = content[:3000]  # 每个文件最多3000字符

        # 构建结构化文件树（初始无标注，后续按需生成）
        file_tree_json = build_file_tree_json(file_paths, annotations={})
        return {
            "source_name": source_name,
            "file_tree": tree_str,
            "language": lang,
            "framework": framework,
            "dependencies": dependencies,
            "entry_points": entry_points,
            "license": license_type,
            "code_snippets": code_snippets,
            "has_examples": any("example" in p.lower() or "demo" in p.lower() for p in file_paths),
            "file_contents": file_contents,
            "file_tree_json": file_tree_json,
            "all_files": file_paths
        }