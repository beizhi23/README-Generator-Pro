import os
from typing import List, Dict, Set, Optional
IGNORE_DIRS: Set[str] = {
    '__pycache__', '.git', '.venv', 'venv', 'env', 'node_modules',
    '.cache', '.idea', '.vscode', 'dist', 'build', 'target',
    '.pytest_cache', '.mypy_cache', '.ruff_cache',
    # 模型 / 预训练权重目录（常见命名）
    'transformers', 'models', 'pretrained_models', 'bert', 'qwen',
    'llama', 'gpt', 't5', 'vit', 'resnet', 'checkpoints', 'weights'
}

IGNORE_FILE_EXTS: Set[str] = {
    '.bin', '.pth', '.pt', '.safetensors', '.h5', '.pb', '.onnx',
    '.ckpt', '.pkl', '.joblib', '.npy', '.npz', '.model', '.weights',
    '.pickle', '.parquet', '.arrow', '.msgpack'
}

# 视为文本文件的扩展名（会尝试读取内容）
TEXT_EXTS: Set[str] = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md', '.txt',
    '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.xml',
    '.html', '.css', '.scss', '.sql', '.sh', '.bat', '.ps1',
    '.rb', '.go', '.rs', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.php', '.swift', '.kt', '.kts', '.scala', '.lua',
    '.pl', '.pm', '.r', '.R', '.jl'
}

MAX_FILE_SIZE_MB = 5   # 超过此大小的文件不读取内容，也不显示在文件树中

def is_path_ignored(path: str) -> bool:
    """检查文件路径中是否包含应忽略的目录名"""
    parts = path.split('/')
    # 检查目录部分（除了文件名本身）
    for part in parts[:-1]:
        if part in IGNORE_DIRS:
            return True
    return False

def should_ignore_dir(dir_name: str) -> bool:
    """判断是否应忽略整个目录（及其子内容）"""
    return dir_name in IGNORE_DIRS


def should_ignore_file(file_name: str, file_size: int = 0) -> bool:
    """判断是否应忽略文件（不加入文件树，不读取内容）"""
    ext = os.path.splitext(file_name)[1].lower()
    if ext in IGNORE_FILE_EXTS:
        return True
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return True
    return False


def is_text_file(file_name: str) -> bool:
    """判断文件扩展名是否为可读取的文本文件"""
    ext = os.path.splitext(file_name)[1].lower()
    return ext in TEXT_EXTS

def detect_programming_language(file_paths: List[str]) -> str:
    ext_map = {'.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.go': 'Go',
               '.rs': 'Rust', '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.rb': 'Ruby'}
    ext_counts = {}
    for path in file_paths:
        ext = os.path.splitext(path)[1]
        if ext in ext_map:
            ext_counts[ext_map[ext]] = ext_counts.get(ext_map[ext], 0) + 1
    if ext_counts:
        return max(ext_counts, key=ext_counts.get)
    return "Unknown"

def detect_framework(file_paths: List[str], contents: Dict) -> str:
    # 基于文件或依赖简单识别
    if 'requirements.txt' in contents:
        if 'fastapi' in contents['requirements.txt'].lower():
            return 'FastAPI'
        if 'django' in contents['requirements.txt'].lower():
            return 'Django'
    if 'package.json' in contents:
        if '"react"' in contents['package.json']:
            return 'React'
        if '"express"' in contents['package.json']:
            return 'Express.js'
    return "通用框架"

def parse_dependencies(filename: str, content: str) -> Dict:
    # 简化实现
    if filename == 'requirements.txt':
        deps = [line.strip().split('==')[0] for line in content.split('\n') if line.strip() and not line.startswith('#')]
        return {"python": deps[:5]}
    elif filename == 'package.json':
        import json
        try:
            data = json.loads(content)
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            return {"node": list(deps.keys())[:5]}
        except:
            pass
    return {}

def identify_entry_points(file_paths: List[str]) -> List[str]:
    candidates = ['main.py', 'app.py', 'index.js', 'server.js', 'main.go', 'src/main.rs', 'Main.java']
    for cand in candidates:
        if cand in file_paths:
            return [cand]
    # 启发式：根目录下 .py 文件
    py_files = [p for p in file_paths if p.endswith('.py') and '/' not in p]
    return py_files[:1] if py_files else []

def generate_file_tree(file_paths: List[str], key_files: Dict) -> str:
    # 简单树形展示
    tree = []
    for path in sorted(file_paths):
        indent = "  " * path.count('/')
        name = os.path.basename(path)
        if path in key_files:
            name += f"  # {key_files[path]}"
        tree.append(f"{indent}- {name}")
    return "\n".join(tree[:50])  # 限制长度

def extract_license_type(license_path: str, content: str) -> str:
    if not content:
        return "未知"
    content_lower = content.lower()
    if "mit" in content_lower:
        return "MIT"
    if "apache" in content_lower:
        return "Apache 2.0"
    if "gpl" in content_lower:
        return "GPL"
    return "其他"

def build_file_tree_json(file_paths: list, annotations: dict = None) -> dict:
    """将文件路径列表转换为嵌套字典结构，支持标注"""
    tree = {}
    for path in sorted(file_paths):
        parts = path.split('/')
        node = tree
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                node[part] = {
                    "type": "file",
                    "path": path,
                    "annotation": annotations.get(path, "") if annotations else ""
                }
            else:
                if part not in node:
                    node[part] = {"type": "dir", "children": {}}
                node = node[part]["children"]
    return tree