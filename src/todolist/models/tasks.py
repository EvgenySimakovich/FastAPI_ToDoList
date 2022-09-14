from enum import Enum
from pydantic import BaseModel


class TaskAction(str, Enum):
    OPEN = 'open'
    CLOSE = 'close'


class TaskBase(BaseModel):
    title: str
    description: str | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    is_complete: bool


class Task(TaskBase):
    id: int
    is_complete: bool

    class Config:
        orm_mode = True
