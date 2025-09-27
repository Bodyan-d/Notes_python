from fastapi import FastAPI, Depends, HTTPException
from typing import List
from enum import IntEnum
import sqlite3
import uuid
from src.validation import Task, TaskCreate, TaskUpdate
from src.helpers import get_db

SELECT_ALL= "SELECT * FROM tasks WHERE task_id=:task_id"
ERROR_404 = "Task not found"

app = FastAPI() 

conn = sqlite3.connect('tasks.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    task_name TEXT,
    task_desc TEXT,
    priority INTEGER,
    progres TEXT
)
""")
conn.commit()
conn.close()

@app.get("/")
def get_root():
    return {"Project Name": "Tasks API"}


@app.get("/tasks", response_model=List[Task])
def get_tasks(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    return [
        Task(
            task_id=row[0],
            task_name=row[1],
            task_desc=row[2],
            priority=row[3],
            progres=row[4]
        )
        for row in rows
    ]

@app.post("/tasks")
def create_task(task: TaskCreate, db: sqlite3.Connection = Depends(get_db)):
    new_id = str(uuid.uuid4())
    
    
    new_task = {
    "task_id": new_id,
    "task_name": task.task_name,
    "task_desc": task.task_desc,
    "priority": task.priority.value,
    "progres": task.progres.value
    }
    
    cursor = db.cursor()
    cursor.execute("INSERT INTO tasks VALUES (:task_id, :task_name, :task_desc, :priority, :progres)", new_task)
    db.commit()
    cursor.execute(SELECT_ALL, {"task_id": new_id})
    row = cursor.fetchone()
    return Task(
            task_id=row[0],
            task_name=row[1],
            task_desc=row[2],
            priority=row[3],
            progres=row[4]
        )


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(SELECT_ALL, {"task_id": task_id})
    row = cursor.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail=ERROR_404)
    return Task(
            task_id=row[0],
            task_name=row[1],
            task_desc=row[2],
            priority=row[3],
            progres=row[4]
        )
        
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, updated_task: TaskUpdate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    cursor.execute("SELECT task_id, task_name, task_desc, priority, progres FROM tasks WHERE task_id = :task_id", {"task_id": task_id})
    existing_row = cursor.fetchone()
    if existing_row is None:
        raise HTTPException(status_code=404, detail=ERROR_404)
    
    update_data = {
        k: (v.value if isinstance(v, IntEnum) else v)
        for k, v in updated_task.model_dump(exclude_unset=True).items()
    }
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    
    set_clause = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
    update_data["task_id"] = task_id

    cursor.execute(f"UPDATE tasks SET {set_clause} WHERE task_id = :task_id", update_data)

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail=ERROR_404)

    db.commit()

    cursor.execute("SELECT * FROM tasks WHERE task_id = :task_id", {"task_id": task_id})
    row = cursor.fetchone()
    
    return Task(
        task_id=row[0],
        task_name=row[1],
        task_desc=row[2],
        priority=row[3],
        progres=row[4]
    )
    

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    cursor.execute(SELECT_ALL, {"task_id": task_id})
    row = cursor.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail=ERROR_404)
    
    cursor.execute("DELETE FROM tasks WHERE task_id=:task_id", {"task_id": task_id})
    db.commit()
    
    return Task(
        task_id=row[0],
        task_name=row[1],
        task_desc=row[2],
        priority=row[3],
        progres=row[4]
    )
    
    


