from fastapi import FastAPI, Body
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

api = FastAPI()

enable_multi_threaded = {"check_same_thread": False}
tasks_db = sqlite3.connect("tasks.db", **enable_multi_threaded)
# tasks_db = sqlite3.connect("tasks.db", check_same_thread=False)

# Create/connect to DB + table
tasks_query = tasks_db.cursor()
id_properties = "INTEGER PRIMARY KEY AUTOINCREMENT"
title_properties = "TEXT NOT NULL"

tasks_query.execute(f"""
 CREATE TABLE IF NOT EXISTS tasks (
 id {id_properties},
 title {title_properties}
 )
""")
tasks_db.commit()

@api.get("/")
def read_root():
    return{"message": "Hello, legend! Back-end's live with xAI power & SQLite!"}

@api.get("/tasks")
def get_tasks():
    tasks_query.execute("SELECT id, title FROM tasks")
    columns = tasks_query.fetchall()
    
    tasks = []                    # initialize empty list
    
    for col in columns:
        task = {
            "id": col[0],         # first column
            "title": col[1]       # second column
        }
        tasks.append(task)
    
    return tasks

@api.post("/tasks")
def create_task(task: dict = Body(...)):
 
 title = task.get("title")

 if not title:
    return {"error": "No title provided"}
 
 tasks_query.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
 tasks_db.commit()
 return {"message": "Task created!", "new_task": {"title": title}}

@api.delete("/tasks/{task_id}")
def delete_task(task_id: int):
 
 tasks_query.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
 if tasks_query.fetchone() is None:
    return {"error": "Task not found"}

 tasks_query.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
 tasks_db.commit()
 return {"message": f"Task {task_id} deleted!"}

@api.put("/tasks/{task_id}")
def update_task(task_id: int, task: dict = Body(...)):
 new_title = task.get("title")
 if not new_title:
    return {"error": "No title provided"}

 tasks_query.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
 if tasks_query.fetchone() is None:
    return {"error": "Task not found"}

 tasks_query.execute("UPDATE tasks SET title = ? WHERE id = ?", (new_title, task_id))
 tasks_db.commit()
 return {"message": f"Task {task_id} updated!", "new_title": new_title}

# Resolve CORS
# List exact allowed origins — avoid "*" if using credentials/cookies
origins = [
    "https://*.vercel.app",             # optional: covers preview branches
    "http://localhost:3000",            # keep for local dev
    "http://localhost:5173",            # if using Vite
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,             # set False if you don't use cookies/auth
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["*"],               # if you need custom response headers
    max_age=600,                        # cache preflight responses
)