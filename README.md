Task Manager

STACK: FastAPI, Postgresql, Pytest

FUNCTIONS:
1. Create task
2. Get Task id 
3. Get full list Task or list Task by status
4. Edit Task by id
5. Delete Task by id

LAUNCH: 
1. setup python 3.10+
2. git clone https://github.com/qwiixx/TaskManager.git
3. python -m venv venv
4. source venv/bin/activate   # Linux/macOS or venv\Scripts\activate      # Windows
5. pip install -r requirements.txt
6. uvicorn app.main:app --reload


Swagger-docs: after launch http://127.0.0.1:8000/docs
