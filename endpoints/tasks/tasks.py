from fastapi import APIRouter, Response, status
from database import connection
from uuid import uuid4
from endpoints.tasks.models import *

router = APIRouter(prefix="/api/tasks")


@router.get("")
async def get_tasks():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return list(dict(zip(task_model, task)) for task in result)


@router.get("/{user_id}/{project_id}/{task_id}")
async def get_task(user_id: str, project_id: str, task_id: str, response: Response):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE user_id = %s AND project_id = %s",
        (
            user_id,
            project_id,
        ),
    )
    result = cursor.fetchone()

    if not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "project not found"}

    cursor.execute(
        "SELECT * FROM tasks WHERE project_id = %s AND task_id = %s",
        (
            project_id,
            task_id,
        ),
    )
    task = cursor.fetchone()

    cursor.close()
    conn.close()

    if not task:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "task not found"}

    return dict(zip(task_model, task))


@router.get("/{user_id}")
async def get_user_tasks(user_id: str, response: Response):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE user_id = %s", (user_id,))
    projects = cursor.fetchall()
    if not projects:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "no projects found for current user"}
    tasks = []
    for project in projects:
        cursor.execute("SELECT * FROM tasks WHERE project_id = %s", (project[0],))
        tasks += cursor.fetchall()
    cursor.close()
    conn.close()
    return list(dict(zip(task_model, task)) for task in tasks)


@router.get("/{user_id}/{project_id}")
async def get_project_tasks(user_id: str, project_id: str, response: Response):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * from tasks WHERE project_id = %s ",
        (project_id,),
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return list(dict(zip(task_model, task)) for task in result)


@router.post("/{user_id}/{project_id}")
async def create_task(user_id: str, project_id: str, task: NewTask, response: Response):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE user_id = %s AND project_id = %s",
        (user_id, project_id),
    )
    result = cursor.fetchone()

    if not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "project not found"}

    task_id = str(uuid4())
    cursor.execute(
        "INSERT INTO tasks (task_id, project_id, title, description, due_date, priority, completed) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (
            task_id,
            project_id,
            task.title,
            task.description,
            task.due_date,
            task.priority,
            task.completed,
        ),
    )
    conn.commit()
    cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if not result:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "something went wrong with the database"}

    return dict(zip(task_model, result))


@router.put("/{user_id}/{project_id}/{task_id}")
async def update_task(
    user_id: str, project_id: str, task_id: str, task: UpdateTask, response: Response
):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE user_id = %s AND project_id = %s",
        (
            user_id,
            project_id,
        ),
    )
    result = cursor.fetchone()

    if not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "project not found"}

    cursor.execute(
        "SELECT * FROM tasks WHERE project_id = %s AND task_id = %s",
        (
            project_id,
            task_id,
        ),
    )
    result = cursor.fetchone()
    if not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "task not found"}
    title = task.title if task.title is not None else result[2]
    description = task.description if task.description is not None else result[3]
    due_date = task.due_date if task.due_date is not None else result[4]
    priority = task.priority if task.priority is not None else result[5]
    completed = task.completed if task.completed is not None else result[6]
    print(task)

    cursor.execute(
        "UPDATE tasks SET title = %s, description = %s, due_date = %s, priority = %s, completed = %s WHERE task_id = %s",
        (
            title,
            description,
            due_date,
            priority,
            completed,
            task_id,
        ),
    )
    conn.commit()
    cursor.execute(
        "SELECT * FROM tasks WHERE project_id = %s AND task_id = %s",
        (
            project_id,
            task_id,
        ),
    )
    task = cursor.fetchone()
    cursor.close()
    conn.close()

    if not task:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "something went wrong with the database"}
    return dict(zip(task_model, task))


@router.delete("/{user_id}/{project_id}/{task_id}")
async def delete_task(user_id: str, project_id: str, task_id: str, response: Response):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM projects WHERE user_id = %s AND project_id = %s",
        (
            user_id,
            project_id,
        ),
    )
    result = cursor.fetchone()
    if not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "project not found"}

    cursor.execute(
        "SELECT * FROM tasks WHERE task_id = %s AND project_id = %s",
        (
            task_id,
            project_id,
        ),
    )
    result = cursor.fetchone()
    if not result:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "task not found"}
    cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "task deleted successfully"}
