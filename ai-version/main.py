from fastapi import FastAPI, HTTPException, Body, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(
    title="Todo API",
    description="Simple Todo API using In-Memory Storage",
    version="1.0.0",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
        "docExpansion": "list"
    }
)

# -------------------------------
# Initial Data
# -------------------------------

INITIAL_TASKS = [
    {"id": 1, "title": "Learn FastAPI", "completed": False},
    {"id": 2, "title": "Build Todo API", "completed": True},
    {"id": 3, "title": "Read Swagger Docs", "completed": False},
]

tasks = INITIAL_TASKS.copy()


# -------------------------------
# Helper
# -------------------------------

def error_response(message: str, code: int):
    return JSONResponse(
        status_code=code,
        content={"error": message}
    )


# -------------------------------
# Models
# -------------------------------

class Task(BaseModel):
    title: str | None = None
    completed: bool = False


# -------------------------------
# Health Endpoint
# -------------------------------

@app.get("/health", status_code=200)
def health():
    return {
        "status": "OK"
    }


# -------------------------------
# Reset Endpoint
# -------------------------------

@app.post("/reset", status_code=200)
def reset():
    global tasks
    tasks = INITIAL_TASKS.copy()
    return {
        "message": "Tasks reset successfully"
    }


# -------------------------------
# GET ALL TASKS
# -------------------------------

@app.get("/task", status_code=200)
def get_tasks():
    return tasks


# -------------------------------
# GET SINGLE TASK
# -------------------------------

@app.get("/task/{id}", status_code=200)
def get_task(id: int):

    for task in tasks:
        if task["id"] == id:
            return task

    return error_response("Task not found", 404)


# -------------------------------
# CREATE TASK
# -------------------------------

@app.post("/task", status_code=201)
def create_task(task: Task = Body(...)):

    if task.title is None:
        return error_response("Title is required", 400)

    if task.title.strip() == "":
        return error_response("Title cannot be empty", 400)

    new_task = {
        "id": max([t["id"] for t in tasks], default=0) + 1,
        "title": task.title,
        "completed": task.completed
    }

    tasks.append(new_task)

    return new_task


# -------------------------------
# UPDATE TASK
# -------------------------------

@app.put("/task/{id}", status_code=200)
def update_task(id: int, task: Task):

    if task.title is None:
        return error_response("Title is required", 400)

    if task.title.strip() == "":
        return error_response("Title cannot be empty", 400)

    for t in tasks:

        if t["id"] == id:

            t["title"] = task.title
            t["completed"] = task.completed

            return t

    return error_response("Task not found", 404)


# -------------------------------
# DELETE TASK
# -------------------------------

@app.delete("/task/{id}", status_code=200)
def delete_task(id: int):

    for task in tasks:

        if task["id"] == id:
            tasks.remove(task)

            return {
                "message": "Task deleted successfully"
            }

    return error_response("Task not found", 404)