import uuid
from fastapi import APIRouter, Depends, HTTPException
from .taskmanager import TaskManager
from .db import Database
from .models import Task, TaskCreate, TaskUpdate, TaskStatus
from typing import Optional

db = Database(
    host="127.0.0.1",
    port=5432,
    user="postgres",
    password="postgres",
    database="task_db"
)

router = APIRouter()

async def get_manager() -> TaskManager:
    await db.connect() 
    return TaskManager(db)

@router.on_event("startup")
async def startup():
    await db.connect()
    await db.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id UUID PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)

@router.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@router.post("/tasks", response_model=Task)
async def create_task(data: TaskCreate, manager: TaskManager = Depends(get_manager)):
    return await manager.create(data)

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: uuid.UUID, manager: TaskManager = Depends(get_manager)):
    task = await manager.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/tasks", response_model=list[Task])
async def get_tasks(status: Optional[TaskStatus] = None, manager: TaskManager = Depends(get_manager)):
    return await manager.get_list(status=status)

@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: uuid.UUID, data: TaskUpdate, manager: TaskManager = Depends(get_manager)):
    task = await manager.update(task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: uuid.UUID, manager: TaskManager = Depends(get_manager)):
    deleted = await manager.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "deleted"}