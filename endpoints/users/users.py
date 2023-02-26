from fastapi import APIRouter, Response, status
from database import connection
from uuid import uuid4
from endpoints.users.models import *

router = APIRouter(prefix="/api/users")


@router.post("")
async def create_user(user: NewUser, response: Response):
    conn = connection()
    cursor = conn.cursor()
    id = str(uuid4())
    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    result = cursor.fetchone()
    if result:
        cursor.close()
        conn.close()
        response.status_code = status.HTTP_409_CONFLICT
        return {"error": "email already exists"}

    cursor.execute(
        "INSERT INTO users(user_id, name, email, password) VALUES (%s, %s, %s, %s)",
        (id, user.name, user.email, user.password),
    )
    conn.commit()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return dict(zip(user_model, result))
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Something went wrong"}


@router.get("")
async def get_users():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return list(dict(zip(user_model, user)) for user in result)


@router.get("/{user_id}")
async def get_user(user_id: str):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(zip(user_model, result))


@router.post("/signin")
async def signin(user: UserAuth, response: Response):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = %s AND password = %s",
        (
            user.email,
            user.password,
        ),
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return dict(zip(user_model, result))
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "user not found"}


# @router.put("/{user_id}")
# async def update_user(user: NewUser, response: Response):
#     response.status_code = status.HTTP_501_NOT_IMPLEMENTED
#     return {"error": "not implemented yet"}


@router.delete("/{user_id}")
async def delete_user(user_id: str, response: Response):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    if result:
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "user deleted"}
    else:
        cursor.close()
        conn.close()
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "user not found"}
