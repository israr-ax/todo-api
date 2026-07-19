# Task API

A simple in-memory CRUD API for managing a to-do list, built with FastAPI as part of the FlyRank Internship — Backend Track, Week 2.

## What this is

This API lets you create, read, update, and delete tasks (CRUD). Data is stored in memory (a Python list) — it resets every time the server restarts.

## How to run it

1. Clone this repo and navigate into it:
git clone https://github.com/israr-ax/todo-api.git
cd todo-api
2. Create and activate a virtual environment:
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
source venv/bin/activate    # Mac/Linux
3. Install dependencies:
pip install -r requirements.txt
4. Run the server:
5. Open `http://localhost:8000` in your browser, or `http://localhost:8000/docs` for Swagger UI.

## Endpoints

| Method | Path              | Description                        |
|--------|-------------------|-------------------------------------|
| GET    | /                 | API info                           |
| GET    | /health           | Health check                       |
| GET    | /tasks            | List all tasks (supports `?done=` and `?search=`) |
| GET    | /tasks/{id}       | Get a single task                  |
| POST   | /tasks            | Create a new task                  |
| PUT    | /tasks/{id}       | Update a task                      |
| DELETE | /tasks/{id}       | Delete a task                      |
| GET    | /stats            | Task statistics (total/done/open)  |
| POST   | /reset            | Reset tasks to default 3 examples  |

## Example curl output
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{"title":"Test task"}"
HTTP/1.1 201 Created
content-type: application/json
{"id":5,"title":"Test task","done":false}

## Swagger UI

Interactive docs are available at `/docs`.

![Swagger UI screenshot](swagger-screenshot.png)

## The mortality experiment

When the server restarted, only the 3 hardcoded example tasks remained — any tasks created during the session were lost. This happens because data was stored in memory (a Python list), which only exists while the program is running; a database is needed next week to persist data across restarts.

## AI vs me

**My prompt:**
> Create a todo-api on FASTAPI. which have 5 endpoints (GET all tasks, GET one task, POST, PUT and DELETE), when we fire a endpoint it print the exact status codes for every endpoint. it has exact validation rule title missing or empty print the 400. and We dont add any database so we use In-memory storage so add 3 task by your own. Modified the Swagger. For error handling use Error response format use {error: } dont use Fastapi default {detail: }. exact Endpoints paths /task /task{id} /health /reset 

**What the AI did better:**
- Customized actual Swagger UI display settings (expand depth, request duration, doc grouping), not just per-endpoint descriptions.
- Used a `max(id)+1` approach for new task IDs, which is more resilient than a simple counter.

**What it got wrong or quietly ignored:**
- DELETE returned `200` with a message body instead of `204 No Content` — the correct REST convention for deletes.
- PUT required `title` on every call, breaking partial updates (e.g. marking a task done without resending the title).
- Skipped the root `GET /` info endpoint entirely, and didn't add the `?done=`/`?search=` filtering or `/stats` endpoint since I never asked for them.

**What my prompt forgot to specify — and what the AI silently decided:**
- Task field names — I got `done`, the AI chose `completed`.
- Exact success status codes per endpoint — I only specified 400, so the AI guessed 200 for DELETE instead of 204.
- What "print the status code" actually meant — neither of us printed to console; both just returned it in the HTTP response, revealing the phrase was ambiguous.
- My own prompt had an inconsistent path (`/task` singular vs my hand-built `/tasks` plural) — the AI followed it literally rather than catching the mismatch.