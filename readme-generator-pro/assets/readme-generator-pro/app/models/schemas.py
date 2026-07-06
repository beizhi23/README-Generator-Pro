from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class GenerateRequest(BaseModel):
    repo_url: Optional[str] = Field(None)
    user_requirements: Optional[str] = Field(None)
    platform_target: Optional[str] = "github"
    session_id: Optional[str] = None

class ModifyRequest(BaseModel):
    session_id: str
    modification: str
    platform_target: Optional[str] = "github"
    model_name: Optional[str] = None
    api_base: Optional[str] = None

class GenerateResponse(BaseModel):
    session_id: str
    readme_content: str
    file_tree_preview: str
    file_tree_json: dict

class UserSettings(BaseModel):
    api_key: Optional[str] = ""
    api_base: Optional[str] = "https://api.openai.com/v1"
    model_name: Optional[str] = "gpt-3.5-turbo"

class DocumentHistoryItem(BaseModel):
    id: str
    title: str
    readme_content: Optional[str] = None
    project_source: Optional[str] = ""
    platform_target: Optional[str] = "github"
    created_at: Optional[str] = None
