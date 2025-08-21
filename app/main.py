from fastapi import FastAPI
from .db import Database
from .taskmanager import TaskManager
from .routers import router

app = FastAPI()


app.include_router(router)
