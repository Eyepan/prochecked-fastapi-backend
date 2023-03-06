from typing import Optional
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


class UpdateUser(BaseModel):
    name: str
    email: str
    password: str
    newPassword: str


user_model = ["user_id", "name", "email", "password"]
