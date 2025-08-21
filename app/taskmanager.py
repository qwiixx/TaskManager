from .db import Database 
from .models import Task, TaskCreate, TaskStatus, TaskUpdate
import uuid
from typing import Optional, Any, List

class TaskManager():
    def __init__(self, db: Database):
        self.db = db

    async def create(self, data: TaskCreate) -> Task:
        row = await self.db.fetchrow(
            """
            INSERT INTO tasks (id, title, description, status)
            VALUES ($1, $2, $3, $4)
            RETURNING id, title, description, status
            """,
            uuid.uuid4(), data.title, data.description, TaskStatus.CREATED.value,
        )
        return Task(**dict(row))

    async def get(self, task_id: uuid.UUID) -> Optional[Task]:
        row = await self.db.fetchrow(
            "SELECT id, title, description, status FROM tasks WHERE id=$1",
            task_id,
        )
        return Task(**dict(row)) if row else None

    async def get_list(self, status: Optional[TaskStatus] = None) -> List[Task]:
        query = "SELECT id, title, description, status FROM tasks"
        params = []
        if status:
            query += " WHERE status = $1"
            params.append(status.value)
        query += " ORDER BY title LIMIT 20"
        rows = await self.db.fetch(query, *params)
        return [Task(**dict(r)) for r in rows]

    async def update(self, task_id: uuid.UUID, data: TaskUpdate) -> Optional[Task]:
        fields, values = [], []
        for key, value in data.model_dump(exclude_unset=True).items():
            fields.append(f"{key} = ${len(values)+2}")
            values.append(value)

        if not fields:
            return await self.get(task_id)

        row = await self.db.fetchrow(
            f"""
            UPDATE tasks
            SET {", ".join(fields)}
            WHERE id = $1
            RETURNING id, title, description, status
            """,
            task_id, *values
        )
        return Task(**dict(row)) if row else None

    async def delete(self, task_id: uuid.UUID) -> bool:
        result = await self.db.execute("DELETE FROM tasks WHERE id=$1", task_id)
        return result.startswith("DELETE 1")