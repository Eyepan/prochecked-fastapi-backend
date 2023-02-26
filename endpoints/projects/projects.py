from fastapi import APIRouter, Response, status
from database import connection
from uuid import uuid4
from endpoints.projects.models import *


router = APIRouter(prefix="/api/projects")


@router.get("")
async def get_projects():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return list(dict(zip(project_model, project)) for project in result)


@router.get("/{user_id}/{project_id}")
async def get_project(user_id: str, project_id: str, response: Response):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE user_id = %s AND project_id = %s",
        (user_id, project_id),
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return dict(zip(project_model, result))
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "project not found"}


@router.get("/{user_id}")
async def get_user_projects(user_id: str):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE user_id = %s", (user_id,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return list(dict(zip(project_model, project)) for project in result)


@router.post("/{user_id}")
async def add_user_project(user_id: str, project: NewProject, response: Response):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "user not found"}
    id = str(uuid4())
    cursor.execute(
        "INSERT INTO projects(user_id, project_id, title, description, created_at, deadline) VALUES (%s, %s, %s, %s, %s, %s)",
        (
            user_id,
            id,
            project.title,
            project.description,
            project.created_at,
            project.deadline,
        ),
    )
    conn.commit()
    cursor.execute("SELECT * FROM projects WHERE project_id = %s", (id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return dict(zip(project_model, result))
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "something went wrong"}


@router.put("/{user_id}/{project_id}")
async def update_project(
    user_id: str, project_id: str, project: UpdateProject, response: Response
):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE project_id = %s AND user_id = %s",
        (project_id, user_id),
    )
    result = cursor.fetchone()
    if not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "project not found"}
    title = project.title if project.title else result[2]
    description = project.description if project.description else result[3]
    created_at = project.created_at if project.created_at else result[4]
    deadline = project.deadline if project.deadline else result[5]
    cursor.execute(
        "UPDATE projects SET title = %s, description = %s, created_at = %s, deadline = %s WHERE project_id = %s AND user_id = %s",
        (title, description, created_at, deadline, project_id, user_id),
    )
    conn.commit()
    cursor.execute(
        "SELECT * FROM projects WHERE project_id = %s AND user_id = %s",
        (project_id, user_id),
    )
    result = cursor.fetchone()
    desc = [d[0] for d in cursor.description]
    cursor.close()
    conn.close()
    if result:
        return dict(zip(desc, result))
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "something went wrong"}


@router.delete("/{user_id}/{project_id}")
async def delete_project(user_id: str, project_id: str, response: Response):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE project_id = %s AND user_id = %s",
        (project_id, user_id),
    )
    result = cursor.fetchone()
    if not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "project not found"}
    cursor.execute(
        "DELETE FROM projects WHERE project_id = %s AND user_id = %s",
        (project_id, user_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "project deleted successfully"}
