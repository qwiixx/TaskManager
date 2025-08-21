import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.models import TaskCreate, TaskUpdate, TaskStatus, Task
from app.routers import get_manager
from unittest.mock import AsyncMock, patch

@pytest.fixture
def client():
    with TestClient(app) as client:
        # Очистка зависимостей перед каждым тестом
        client.app.dependency_overrides.clear()
        yield client

@pytest.mark.asyncio
async def test_create_task(client):
    mock_manager = AsyncMock()
    client.app.dependency_overrides[get_manager] = lambda: mock_manager  
    task_id = uuid.uuid4()
    mock_manager.create.return_value = Task(
        id=task_id,
        title="Test Task",
        description="Test Description",
        status=TaskStatus.CREATED
    ).model_dump()  

    task_data = TaskCreate(title="Test Task", description="Test Description")
    response = client.post("/tasks", json=task_data.model_dump())  

    assert response.status_code == 200
    task = response.json()
    assert task["title"] == task_data.title
    assert task["description"] == task_data.description
    assert task["status"] == TaskStatus.CREATED.value
    assert "id" in task
    mock_manager.create.assert_called_once_with(task_data)

@pytest.mark.asyncio
async def test_get_task(client):
    mock_manager = AsyncMock()
    client.app.dependency_overrides[get_manager] = lambda: mock_manager
    task_id = uuid.uuid4()
    mock_manager.get.return_value = Task(
        id=task_id,
        title="Test Task",
        description="Test Description",
        status=TaskStatus.IN_PROGRESS
    ).model_dump()

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == str(task_id)
    assert task["title"] == "Test Task"
    assert task["status"] == TaskStatus.IN_PROGRESS.value
    mock_manager.get.assert_called_once_with(task_id)

@pytest.mark.asyncio
async def test_get_tasks_list(client):
    mock_manager = AsyncMock()
    client.app.dependency_overrides[get_manager] = lambda: mock_manager
    mock_manager.get_list.return_value = [
        Task(
            id=uuid.uuid4(),
            title="Task 1",
            description="Desc 1",
            status=TaskStatus.CREATED
        ).model_dump()
    ]

    response = client.get("/tasks")
    assert response.status_code == 200
    tasks_list = response.json()
    assert len(tasks_list) == 1
    assert tasks_list[0]["status"] == TaskStatus.CREATED.value
    mock_manager.get_list.assert_called_once()

@pytest.mark.asyncio
async def test_update_task(client):
    mock_manager = AsyncMock()
    client.app.dependency_overrides[get_manager] = lambda: mock_manager
    task_id = uuid.uuid4()
    mock_manager.update.return_value = Task(
        id=task_id,
        title="Updated Task",
        description="Updated Description",
        status=TaskStatus.DONE
    ).model_dump()

    update_data = TaskUpdate(title="Updated Task", description="Updated Description", status=TaskStatus.DONE)
    response = client.put(f"/tasks/{task_id}", json=update_data.model_dump(exclude_unset=True))

    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["title"] == "Updated Task"
    assert updated_task["description"] == "Updated Description"
    assert updated_task["status"] == TaskStatus.DONE.value
    mock_manager.update.assert_called_once_with(task_id, update_data)

@pytest.mark.asyncio
async def test_delete_task(client):
    mock_manager = AsyncMock()
    client.app.dependency_overrides[get_manager] = lambda: mock_manager
    task_id = uuid.uuid4()
    mock_manager.delete.return_value = True

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json() == {"status": "deleted"}
    mock_manager.delete.assert_called_once_with(task_id)