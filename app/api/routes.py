from app.models.schemas import GenerateResponse, ModifyRequest
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.services.task_manager import task_manager
from app.core.analyzer import ProjectAnalyzer
from app.core.generator import generate_readme, generate_understanding
from app.core.renderer import adapt_markdown_for_platform
from app.services.llm_service import LLMService
import asyncio
import json
import os
import tempfile
import shutil
import zipfile
from typing import List
from app.core.generator import generate_project_html
import logging
logger = logging.getLogger(__name__)


router = APIRouter()
analyzer = ProjectAnalyzer()
sessions = {}

@router.post("/generate", response_model=GenerateResponse)
async def generate_readme_endpoint(
    repo_url: str = Form(None),
    folder_files: List[UploadFile] = File(None),      # 多文件上传（文件夹模式）
    folder_zip: UploadFile = File(None),              # ZIP 文件上传
    user_requirements: str = Form(""),
    platform_target: str = Form("github"),
    model_name: str = Form(None),
    api_base: str = Form(None),
    ignored_files: str = Form("")
):
    session_id = str(uuid.uuid4())
    temp_dir = None

    try:
        if repo_url:
            project_info = await analyzer.analyze_github(repo_url)

        elif folder_zip:
            # 处理 ZIP 上传
            if not folder_zip.filename.endswith('.zip'):
                raise HTTPException(400, "请上传 .zip 格式的工程文件夹")
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, folder_zip.filename)
            with open(zip_path, "wb") as f:
                shutil.copyfileobj(folder_zip.file, f)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_dir)
            # 查找解压后的根目录（如果 ZIP 包含一个顶层文件夹则进入，否则直接用 temp_dir）
            extracted_items = os.listdir(temp_dir)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
                project_root = os.path.join(temp_dir, extracted_items[0])
            else:
                project_root = temp_dir
            project_info = analyzer.analyze_folder(project_root)


        elif folder_files:
            ignored_paths = json.loads(ignored_files) if ignored_files else []
            # 处理文件夹上传
            temp_dir = tempfile.mkdtemp()
            for file in folder_files:
                rel_path = file.filename
                safe_path = os.path.normpath(rel_path).lstrip('/')
                if safe_path.startswith('..'):
                    continue
                full_path = os.path.join(temp_dir, safe_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
            # 分析时传入忽略路径列表
            project_info = analyzer.analyze_folder(temp_dir, ignored_paths=ignored_paths)

        else:
            raise HTTPException(400, "请提供 repo_url 或上传文件夹/ZIP")

        # 生成 README
        raw_readme = await generate_readme(
            project_info,
            user_requirements,
            platform_target,
            model_name=model_name,
            api_base=api_base
        )
        adapted_readme = adapt_markdown_for_platform(raw_readme, platform_target)

        # 存储会话，同时保存模型配置以便修改时复用
        sessions[session_id] = {
            "project_info": project_info,
            "last_readme": adapted_readme,
            "history": [user_requirements],
            "model_name": model_name,
            "api_base": api_base,
            "chat_history": []  # 存储聊天记录
        }

        return GenerateResponse(
            session_id=session_id,
            readme_content=adapted_readme,
            file_tree_preview=project_info.get("file_tree", ""),
            file_tree_json=project_info.get("file_tree_json", {})
        )

    finally:
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


@router.post("/modify", response_model=GenerateResponse)
async def modify_readme(req: ModifyRequest):
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(404, "会话不存在")

    # 优先使用请求中的模型配置，否则使用会话中保存的配置
    model_name = req.model_name or session.get("model_name")
    api_base = req.api_base or session.get("api_base")

    new_readme = await generate_readme(
        session["project_info"],
        user_requirements=req.modification,
        platform=req.platform_target,
        model_name=model_name,
        api_base=api_base
    )
    adapted = adapt_markdown_for_platform(new_readme, req.platform_target)
    session["last_readme"] = adapted
    session["history"].append(req.modification)

    return GenerateResponse(
        session_id=req.session_id,
        readme_content=adapted,
        file_tree_preview=session["project_info"].get("file_tree", ""),
        file_tree_json=session["project_info"].get("file_tree_json", {})
    )

@router.post("/chat")
async def chat_with_project(session_id: str, question: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    llm = LLMService()
    answer = await llm.chat_with_project(
        session["project_info"],
        question,
        history=session.get("chat_history", []),
        model=session.get("model_name"),
        api_base=session.get("api_base")
    )
    # 保存对话历史
    session.setdefault("chat_history", []).append({"question": question, "answer": answer})
    return {"answer": answer}

@router.post("/understanding")
async def generate_understanding_endpoint(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    content = await generate_understanding(
        session["project_info"],
        model_name=session.get("model_name"),
        api_base=session.get("api_base")
    )
    return {"content": content}

@router.get("/file_content")
async def get_file_content(session_id: str, file_path: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "会话不存在")
    file_contents = session["project_info"].get("file_contents", {})
    content = file_contents.get(file_path, "文件内容未获取或为空")
    # 可选：生成该文件的功能注释（简单调用 LLM 或使用缓存）
    annotation = session["project_info"].get("file_annotations", {}).get(file_path)
    if not annotation and content and len(content) > 20:
        # 按需生成注释（简单调用 LLM，此处可优化为异步任务）
        try:
            llm = LLMService()
            prompt = f"请用简明扼要（100字以内）说明文件 {file_path} 的主要功能。代码片段：\n{content}"
            annotation = await llm.generate_readme(prompt, model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"), api_base=session.get("api_base"))
            # 缓存
            session["project_info"].setdefault("file_annotations", {})[file_path] = annotation
        except:
            annotation = "暂无注释"
    return {"content": content, "annotation": annotation}


@router.post("/generate-task")
async def submit_generate_task(
        repo_url: str = Form(None),
        folder_files: List[UploadFile] = File(None),
        folder_zip: UploadFile = File(None),
        user_requirements: str = Form(""),
        platform_target: str = Form("github"),
        model_name: str = Form(None),
        api_base: str = Form(None),
        ignored_files: str = Form("")
):
    # 参数验证
    if not repo_url and not folder_zip and not folder_files:
        raise HTTPException(400, "请提供 repo_url 或上传文件夹/ZIP")

    task_id = task_manager.create_task("generate_readme")
    temp_root = None   # 用于记录需要清理的临时目录

    try:
        # 情况1：GitHub 仓库
        if repo_url:
            task_manager.tasks[task_id]["params"] = {
                "type": "repo",
                "repo_url": repo_url,
                "user_requirements": user_requirements,
                "platform_target": platform_target,
                "model_name": model_name,
                "api_base": api_base
            }

        # 情况2：ZIP 文件上传
        elif folder_zip:
            # 创建临时目录
            temp_root = tempfile.mkdtemp()
            zip_path = os.path.join(temp_root, folder_zip.filename)
            # 保存 ZIP 文件
            with open(zip_path, "wb") as f:
                shutil.copyfileobj(folder_zip.file, f)
            # 解压
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(temp_root)
            # 确定解压后的项目根目录
            extracted_items = os.listdir(temp_root)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_root, extracted_items[0])):
                project_root = os.path.join(temp_root, extracted_items[0])
            else:
                project_root = temp_root

            task_manager.tasks[task_id]["params"] = {
                "type": "folder",
                "project_root": project_root,
                "temp_root": temp_root,
                "ignored_paths": [],   # ZIP 无法前端预过滤，后端解压后会再过滤一次
                "user_requirements": user_requirements,
                "platform_target": platform_target,
                "model_name": model_name,
                "api_base": api_base
            }

        # 情况3：文件夹上传（多文件）
        elif folder_files:
            # 解析前端传来的忽略文件列表
            ignored_paths = json.loads(ignored_files) if ignored_files else []
            temp_root = tempfile.mkdtemp()
            for file in folder_files:
                rel_path = file.filename
                # 安全加固：防止路径遍历攻击
                safe_path = os.path.normpath(rel_path).lstrip('/')
                if safe_path.startswith('..'):
                    continue
                full_path = os.path.join(temp_root, safe_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)

            task_manager.tasks[task_id]["params"] = {
                "type": "folder",
                "project_root": temp_root,
                "temp_root": temp_root,
                "ignored_paths": ignored_paths,   # 存储前端过滤的文件路径
                "user_requirements": user_requirements,
                "platform_target": platform_target,
                "model_name": model_name,
                "api_base": api_base
            }

        # 启动后台任务
        asyncio.create_task(_run_generate_task(task_id))
        return {"task_id": task_id}

    except Exception as e:
        # 如果初始化过程中出错，立即清理临时目录
        if temp_root and os.path.exists(temp_root):
            shutil.rmtree(temp_root, ignore_errors=True)
        raise HTTPException(500, f"准备任务失败: {str(e)}")

@router.post("/modify-task")
async def submit_modify_task(
        session_id: str,
        modification: str,
        platform_target: str = "github",
        model_name: str = None,
        api_base: str = None
):
    """提交修改 README 的后台任务"""
    from app.api.routes import sessions  # 注意：原有 sessions 字典在模块顶部，需要导入

    if session_id not in sessions:
        raise HTTPException(404, "会话不存在")

    task_id = task_manager.create_task("modify_readme")
    task_manager.tasks[task_id]["params"] = {
        "session_id": session_id,
        "modification": modification,
        "platform_target": platform_target,
        "model_name": model_name,
        "api_base": api_base
    }
    asyncio.create_task(_run_modify_task(task_id))
    return {"task_id": task_id}


@router.get("/task/{task_id}/stream")
async def task_progress_stream(task_id: str):
    """SSE 端点：推送任务进度和最终结果"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(404, "任务不存在")

    async def event_generator():
        last_event_id = 0
        while True:
            task = task_manager.get_task(task_id)
            if not task:
                break

            # 获取新事件
            events = task_manager.get_events_since(task_id, last_event_id)
            for evt in events:
                yield f"data: {json.dumps(evt)}\n\n"
                last_event_id += 1

            # 如果任务完成或失败，退出
            if task["status"] in ("completed", "failed"):
                # 发送最终结果
                if task["status"] == "completed":
                    final_event = {
                        "progress": 100,
                        "message": "完成",
                        "result": task["result"],
                        "status": "completed"
                    }
                    yield f"data: {json.dumps(final_event)}\n\n"
                else:
                    error_event = {
                        "progress": task["progress"],
                        "message": task["message"],
                        "error": task["error"],
                        "status": "failed"
                    }
                    yield f"data: {json.dumps(error_event)}\n\n"
                break

            await asyncio.sleep(0.3)  # 轮询间隔

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def _run_generate_task(task_id: str):
    """后台执行生成 README 的完整流程，并更新进度"""
    params = task_manager.tasks[task_id]["params"]
    temp_root = params.get("temp_root")   # 可能为 None（仓库模式）
    try:
        # 阶段1: 分析项目 (0% -> 40%)
        task_manager.update_progress(task_id, 5, "正在准备分析环境...")
        await asyncio.sleep(0.1)

        if params["type"] == "repo":
            task_manager.update_progress(task_id, 10, "正在从 GitHub 获取仓库信息...")
            project_info = await analyzer.analyze_github(params["repo_url"])
        else:  # folder
            task_manager.update_progress(task_id, 10, "正在分析项目结构...")
            # 获取忽略路径列表（前端预过滤的文件）
            ignored_paths = params.get("ignored_paths", [])
            project_info = analyzer.analyze_folder(params["project_root"], ignored_paths=ignored_paths)

        task_manager.update_progress(task_id, 40, "项目分析完成，正在准备生成 README...")

        # 阶段2: 调用 LLM 生成 README (40% -> 90%)
        task_manager.update_progress(task_id, 50, "正在调用 AI 模型生成文档内容...")

        raw_readme = await generate_readme(
            project_info,
            params["user_requirements"],
            params["platform_target"],
            model_name=params["model_name"],
            api_base=params["api_base"]
        )

        task_manager.update_progress(task_id, 85, "AI 生成完成，正在进行平台适配...")

        # 阶段3: 平台适配 (90% -> 100%)
        adapted_readme = adapt_markdown_for_platform(raw_readme, params["platform_target"])

        # 存储会话（与原有 sessions 兼容）
        from app.api.routes import sessions
        import uuid
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "project_info": project_info,
            "last_readme": adapted_readme,
            "history": [params["user_requirements"]],
            "model_name": params["model_name"],
            "api_base": params["api_base"],
            "chat_history": []
        }

        result = {
            "session_id": session_id,
            "readme_content": adapted_readme,
            "file_tree_preview": project_info.get("file_tree", ""),
            "file_tree_json": project_info.get("file_tree_json", {})
        }
        task_manager.complete_task(task_id, result)

    except Exception as e:
        task_manager.fail_task(task_id, str(e))
    finally:
        # 清理临时目录（仅当存在 temp_root 时）
        if temp_root and os.path.exists(temp_root):
            shutil.rmtree(temp_root, ignore_errors=True)


async def _run_modify_task(task_id: str):
    """后台执行修改 README"""
    from app.api.routes import sessions
    from app.core.generator import generate_readme
    from app.core.renderer import adapt_markdown_for_platform

    params = task_manager.tasks[task_id]["params"]
    session_id = params["session_id"]

    try:
        if session_id not in sessions:
            raise ValueError("会话不存在")

        session = sessions[session_id]
        task_manager.update_progress(task_id, 20, "正在根据修改指令重新生成...")

        model_name = params["model_name"] or session.get("model_name")
        api_base = params["api_base"] or session.get("api_base")

        new_readme = await generate_readme(
            session["project_info"],
            user_requirements=params["modification"],
            platform=params["platform_target"],
            model_name=model_name,
            api_base=api_base
        )

        task_manager.update_progress(task_id, 70, "正在适配平台...")
        adapted = adapt_markdown_for_platform(new_readme, params["platform_target"])
        session["last_readme"] = adapted
        session["history"].append(params["modification"])

        result = {
            "session_id": session_id,
            "readme_content": adapted,
            "file_tree_preview": session["project_info"].get("file_tree", ""),
            "file_tree_json": session["project_info"].get("file_tree_json", {})
        }
        task_manager.complete_task(task_id, result)
    except Exception as e:
        task_manager.fail_task(task_id, str(e))


@router.post("/generate_html_page")
async def generate_html_page(
    session_id: str = Form(...),          # 必须使用 Form
    github_url: str = Form(None)          # 可选字段同样使用 Form
):
    """生成项目介绍 HTML 页面（论文风格）"""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "会话不存在或已过期")

    # 如果没有提供 github_url，尝试从 project_info 中提取
    if not github_url:
        source = session["project_info"].get("source_name", "")
        if "github.com" in source:
            github_url = source
        else:
            github_url = "#"

    model_name = session.get("model_name")
    api_base = session.get("api_base")

    try:
        html_content = await generate_project_html(
            session["project_info"],
            github_url=github_url,
            model_name=model_name,
            api_base=api_base
        )
        return {"html_content": html_content}
    except Exception as e:
        logger.error(f"生成 HTML 页面失败: {e}")
        raise HTTPException(500, f"生成失败: {str(e)}")