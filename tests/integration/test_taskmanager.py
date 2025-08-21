import pytest
import pytest_asyncio
import uuid
from app.db import Database
from app.taskmanager import TaskManager
from app.models import TaskCreate, TaskUpdate, TaskStatus

@pytest_asyncio.fixture  
async def test_db():
    test_db = Database(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database="test_task_db"
    )
    await test_db.connect()
    await test_db.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id UUID PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)
    
    await test_db.execute("DELETE FROM tasks")
    
    yield test_db
    
    await test_db.execute("DROP TABLE IF EXISTS tasks")
    await test_db.disconnect()

@pytest_asyncio.fixture  
async def task_manager(test_db):
    return TaskManager(test_db)

@pytest.mark.asyncio
async def test_create_task(task_manager):
    task_data = TaskCreate(title="Test Task", description="Test Description")
    created_task = await task_manager.create(task_data)
    
    assert created_task.title == task_data.title
    assert created_task.description == task_data.description
    assert created_task.status == TaskStatus.CREATED
    assert isinstance(created_task.id, uuid.UUID)
    
    retrieved_task = await task_manager.get(created_task.id)
    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id

@pytest.mark.asyncio
async def test_get_task(task_manager):
    task_data = TaskCreate(title="Test Task", description="Test Description")
    created_task = await task_manager.create(task_data)
    
    retrieved_task = await task_manager.get(created_task.id)
    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.title == task_data.title
    assert retrieved_task.status == TaskStatus.CREATED

    non_existent_id = uuid.uuid4()
    retrieved_none = await task_manager.get(non_existent_id)
    assert retrieved_none is None

@pytest.mark.asyncio
async def test_get_list(task_manager):
    tasks = [
        TaskCreate(title=f"Task {i}", description=f"Desc {i}")
        for i in range(3)
    ]
    for task in tasks:
        await task_manager.create(task)
    
    task_list = await task_manager.get_list()
    assert len(task_list) == 3
    for task in task_list:
        assert task.status == TaskStatus.CREATED
        assert task.title in [t.title for t in tasks]
    
    filtered_list = await task_manager.get_list(status=TaskStatus.CREATED)
    assert len(filtered_list) == 3
    assert all(task.status == TaskStatus.CREATED for task in filtered_list)

@pytest.mark.asyncio
async def test_update_task(task_manager):
    task_data = TaskCreate(title="Original Task", description="Original Description")
    created_task = await task_manager.create(task_data)
    
    update_data = TaskUpdate(title="Updated Task", description="Updated Description", status=TaskStatus.DONE)
    updated_task = await task_manager.update(created_task.id, update_data)
    
    assert updated_task is not None
    assert updated_task.title == update_data.title
    assert updated_task.description == update_data.description
    assert updated_task.status == TaskStatus.DONE
    
    partial_update = TaskUpdate(status=TaskStatus.IN_PROGRESS)
    updated_partially = await task_manager.update(created_task.id, partial_update)
    assert updated_partially.status == TaskStatus.IN_PROGRESS
    assert updated_partially.title == "Updated Task"
    
    non_existent_id = uuid.uuid4()
    updated_none = await task_manager.update(non_existent_id, update_data)
    assert updated_none is None

@pytest.mark.asyncio
async def test_delete_task(task_manager):
    task_data = TaskCreate(title="Task to Delete", description="Description")
    created_task = await task_manager.create(task_data)
    
    deleted = await task_manager.delete(created_task.id)
    assert deleted is True
    
    retrieved_task = await task_manager.get(created_task.id)
    assert retrieved_task is None
    
    non_existent_id = uuid.uuid4()
    deleted_none = await task_manager.delete(non_existent_id)
    assert deleted_none is False 