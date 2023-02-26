from pydantic import BaseModel


class NewUser(BaseModel):
    name: str
    email: str
    password: str


class UserAuth(BaseModel):
    email: str
    password: str


class User(BaseModel):
    user_id: str
    name: str
    email: str
    password: str


class NewTask(BaseModel):
    project_id: str
    title: str
    description: str | None = None
    due_date: str
    priority: int
    completed: int


user_model = ["user_id", "name", "email", "password"]
