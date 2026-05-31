from pydantic import BaseModel, Field
from typing import Optional

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