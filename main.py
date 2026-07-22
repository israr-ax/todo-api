from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3


DB_FILE = "tasks.db"


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    # only insert defaults if table is empty, otherwise restarting
    # the server would keep adding duplicates
    cur.execute("SELECT COUNT(*) FROM tasks")
    count = cur.fetchone()[0]

    if count == 0:
        default_tasks = [
            ("Buy milk", 0),
            ("Walk the dog", 1),
            ("Finish assignment", 0),
        ]
        cur.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", default_tasks)

    conn.commit()
    conn.close()


init_db()


app = FastAPI(
    title="Task API",
    description="A simple in-memory CRUD API for managing a to-do list.",
    version="1.0"
)

# In-memory "database"
tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Finish assignment", "done": False},
]
next_id = 4  # tracks the next free id


# Custom error format: {"error": "..."} instead of FastAPI's default {"detail": "..."}
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# Shape of the data a client sends in POST /tasks
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/", summary="API info", description="Returns basic info about this API and its endpoints.")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", summary="Health check", description="Confirms the server is running.")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks", description="Returns tasks, optionally filtered by done status or search term.")
def get_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    conn = get_db()
    cur = conn.cursor()

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    return [dict(r) for r in rows]

@app.get("/tasks/{task_id}", summary="Get one task", description="Returns a single task by id, or 404 if not found.")
def get_task(task_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return dict(row)

@app.get("/stats", summary="Task statistics", description="Returns total, done, and open task counts.")
def get_stats():
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    return {
        "total": total,
        "done": done_count,
        "open": total - done_count
    }
    

@app.post("/tasks", status_code=201, summary="Create a task", description="Creates a new task with the given title. Title is required.")
def create_task(task: TaskCreate):
    global next_id
    
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")
    
    new_task = {"id": next_id, "title": task.title, "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task

@app.put("/tasks/{task_id}", summary="Update a task", description="Updates a task's title and/or done status. Unknown id returns 404.")
def update_task(task_id: int, update: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            if update.title is not None:
                if not update.title.strip():
                    raise HTTPException(status_code=400, detail="Title cannot be empty")
                task["title"] = update.title
            if update.done is not None:
                task["done"] = update.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/reset", summary="Reset tasks", description="Restores the original 3 example tasks and clears everything else.")
def reset_tasks():
    global tasks, next_id
    tasks = [
        {"id": 1, "title": "Buy milk", "done": False},
        {"id": 2, "title": "Walk the dog", "done": True},
        {"id": 3, "title": "Finish assignment", "done": False},
    ]
    next_id = 4
    return {"message": "Tasks reset to default"}


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task", description="Removes a task by id. Unknown id returns 404.")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")