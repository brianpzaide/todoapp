import uuid
from enum import Enum
from pydantic import BaseModel
from fastapi_users import schemas


class Status(Enum):
    Todo = 'todo'
    Inprogress = 'in_progress'
    Archive = 'archive'
    Done = "done"

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass

class TodoBase(BaseModel):
    title: str
    description: str
    
    class Config:
        orm_mode = True

class TodoInfo(TodoBase):
    id: int
    status: str

class TodoStatusChange(BaseModel):
    id: int
    status: Status