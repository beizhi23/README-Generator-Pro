# app/services/task_manager.py
import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime


class TaskManager:
    """内存中管理异步任务的状态和进度"""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self, task_type: str) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "task_id": task_id,
            "type": task_type,
            "status": "pending",  # pending, running, completed, failed
            "progress": 0,
            "message": "任务已创建",
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            "events": []  # 存储事件供 SSE 重放
        }
        return task_id

    def update_progress(self, task_id: str, progress: int, message: str, **extra):
        if task_id not in self.tasks:
            return
        self.tasks[task_id]["progress"] = progress
        self.tasks[task_id]["message"] = message
        self.tasks[task_id]["status"] = "running"
        self.tasks[task_id].update(extra)
        # 记录事件（用于 SSE）
        self.tasks[task_id]["events"].append({
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    def complete_task(self, task_id: str, result: Any):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["progress"] = 100
            self.tasks[task_id]["message"] = "完成"
            self.tasks[task_id]["result"] = result
            self.tasks[task_id]["events"].append({
                "progress": 100,
                "message": "完成",
                "timestamp": datetime.now().isoformat()
            })

    def fail_task(self, task_id: str, error: str):
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["error"] = error
            self.tasks[task_id]["message"] = f"失败: {error}"
            self.tasks[task_id]["events"].append({
                "progress": self.tasks[task_id]["progress"],
                "message": f"失败: {error}",
                "timestamp": datetime.now().isoformat()
            })

    def get_task(self, task_id: str) -> Optional[Dict]:
        return self.tasks.get(task_id)

    def get_events_since(self, task_id: str, last_event_id: int = 0) -> list:
        """获取自某个索引之后的事件（简单实现）"""
        task = self.tasks.get(task_id)
        if not task:
            return []
        events = task.get("events", [])
        if last_event_id >= len(events):
            return []
        return events[last_event_id:]


task_manager = TaskManager()