from pydantic import BaseModel
from typing import Optional


class NewTask(BaseModel):
    title: str
    description: str
    due_date: str
    priority: int
    completed: int


class Task(BaseModel):
    task_id: str
    project_id: str
    title: str
    description: str
    due_date: str
    priority: int
    completed: int


class UpdateTask(BaseModel):
    title: Optional[str]
    description: Optional[str]
    due_date: Optional[str]
    priority: Optional[int]
    completed: Optional[int]


task_model = [
    "task_id",
    "project_id",
    "title",
    "description",
    "due_date",
    "priority",
    "completed",
]
