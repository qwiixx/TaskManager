import uuid
from enum import Enum
from pydantic import BaseModel


class TaskStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    status: TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
