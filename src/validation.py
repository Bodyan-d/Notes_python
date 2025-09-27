from enum import IntEnum, Enum
from pydantic import BaseModel, Field
from typing import Optional

class Priority(IntEnum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

class Progres(str, Enum): 
    TO_DO = "To do"
    IN_PROGRES = "In progres"
    DONE = "Done"
    
class TaskBase(BaseModel):
    task_name: str = Field(..., min_length=3, max_length=256, description="Name of the task") 
    task_desc: str = Field(..., description="Description of the task")
    priority: Priority = Field(default=Priority.LOW, description="Priority of the task")
    progres: Progres = Field(default=Progres.TO_DO, description="Progres of the task")
    
    
class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    task_id: str = Field(..., description="Unique identifier of the task")

class TaskUpdate(TaskBase):
    task_name: Optional[str] = Field(None, min_length=3, max_length=256, description="Name of the task") 
    task_desc: Optional[str] = Field(None, description="Description of the task")
    priority: Optional[Priority] = Field(None, description="Priority of the task")
    progres: Optional[Progres] = Field(None, description="Progres of the task")