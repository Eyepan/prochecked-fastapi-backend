from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints.users import users
from endpoints.projects import projects
from endpoints.tasks import tasks
from database import initDB
import uvicorn

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.on_event("startup")
async def init():
    initDB()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
