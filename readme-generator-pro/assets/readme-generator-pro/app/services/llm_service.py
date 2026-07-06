import os
import logging
from openai import AsyncOpenAI
from typing import Optional

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.default_api_base = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
        self.default_model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        use_mock_env = os.getenv("USE_MOCK_LLM", "").lower()

        # 自动降级逻辑：如果没有 API Key 且未显式关闭 Mock，则启用 Mock
        if not self.api_key:
            if use_mock_env == "false":
                logger.warning("LLM_API_KEY 未设置且 USE_MOCK_LLM=false，将强制启用 Mock 模式以便演示")
            self.use_mock = True
            logger.info("未检测到 LLM_API_KEY，已自动启用 Mock 模式（USE_MOCK_LLM=true）")
        else:
            self.use_mock = use_mock_env == "true"

    def _get_client(self, api_base: Optional[str] = None):
        if self.use_mock:
            raise RuntimeError("当前处于 Mock 模式，不应调用真实 LLM 客户端")
        base = api_base or self.default_api_base
        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置且未处于 Mock 模式")
        return AsyncOpenAI(api_key=self.api_key, base_url=base)

    async def generate_readme(self, prompt: str, model: Optional[str] = None,
                              api_base: Optional[str] = None, max_tokens: int = 8000,
                              api_key: Optional[str] = None) -> str:
        if self.use_mock:
            logger.info("使用 Mock 模式生成 README")
            return self._mock_readme(prompt)

        try:
            key = api_key or self.api_key
            client = self._get_client_with_key(api_base, key)
            selected_model = model or self.default_model
            response = await client.chat.completions.create(
                model=selected_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}，降级为 Mock 模式")
            return f"❌ LLM 调用失败: {str(e)}\n\n" + self._mock_readme(prompt)


    def _mock_readme(self, prompt: str) -> str:
        """生成模拟 README（移除对不存在方法的调用）"""
        # 可选：简单从 prompt 中提取项目名称（演示用）
        project_name = "示例项目"
        # 尝试从 prompt 中找 "项目名称" 相关行（非必须）
        for line in prompt.split('\n'):
            if '项目名称' in line or '项目介绍' in line:
                # 简单取前30个字符作为名称
                project_name = line.strip()[:50]
                break

        return f"""
        # 项目名称（Mock 生成）
    > 注意：当前未配置有效的 LLM API 或已启用 Mock 模式。
    {project_name}
    ## 安装指南
    请参考项目中的依赖文件安装。
    
    ## 快速开始
    ```bash
    # 根据项目入口文件运行
    python main.py
    许可证
    MIT
    """

    async def chat_with_project(self, project_info: dict, question: str, history: list = None, model: str = None,
                                api_base: str = None) -> str:
        """基于项目信息回答用户问题"""
        if self.use_mock:
            return self._mock_chat(question)

        # 构建项目上下文
        context = f"""
    项目名称: {project_info.get('source_name', '未知')}
    主要语言: {project_info.get('language', '未知')}
    框架: {project_info.get('framework', '未知')}
    依赖: {project_info.get('dependencies', {})}
    入口文件: {project_info.get('entry_points', [])}
    许可证: {project_info.get('license', '未知')}

    文件结构（部分）：
    {project_info.get('file_tree', '')}

    关键文件代码片段：
    {project_info.get('code_snippets', {})}
    
    其他文件内容（部分）：
    { {k: v[:500] for k, v in project_info.get('file_contents', {}).items() if k not in project_info.get('entry_points', [])} }
    """
        prompt = f"""你是一个帮助开发者理解陌生项目的助手。根据以下项目信息回答用户的问题。

    {context}

    用户问题: {question}

    请用清晰、简洁的中文回答，尽量给出具体的文件、函数或代码示例。如果信息不足，请说明需要进一步查看哪个文件。
    """
        try:
            client = self._get_client(api_base)
            selected_model = model or self.default_model
            messages = []
            if history:
                for h in history[-5:]:  # 保留最近5轮
                    messages.append({"role": "user", "content": h["question"]})
                    messages.append({"role": "assistant", "content": h["answer"]})
            messages.append({"role": "user", "content": prompt})
            response = await client.chat.completions.create(
                model=selected_model,
                messages=messages,
                temperature=0.5,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return f"抱歉，回答生成失败：{str(e)}"

    def _mock_chat(self, question: str) -> str:
        return f"[Mock] 这是模拟回答。您问的是：{question}\n请配置有效的 LLM_API_KEY 以获得真实回答。"
    def _get_client_with_key(self, api_base: Optional[str] = None, api_key: Optional[str] = None):
        if self.use_mock:
            raise RuntimeError("Mock mode, no real LLM client")
        base = api_base or self.default_api_base
        key = api_key or self.api_key
        if not key:
            raise ValueError("No API key available")
        return AsyncOpenAI(api_key=key, base_url=base)
