from pydantic import BaseModel
from typing import Optional


class NewProject(BaseModel):
    title: str
    description: Optional[str]
    created_at: str
    deadline: str


class Project(BaseModel):
    project_id: str
    title: str
    description: Optional[str]
    created_at: str
    deadline: str


# because no one could use just the project model
class UpdateProject(BaseModel):
    title: Optional[str]
    description: Optional[str]
    created_at: Optional[str]
    deadline: Optional[str]


project_model = [
    "project_id",
    "user_id",
    "title",
    "description",
    "created_at",
    "deadline",
]
