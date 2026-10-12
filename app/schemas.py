from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class TaskCreate(BaseModel):
    title: str= Field(min_length=1, max_length=100)
    description: str | None=None
    priority: Literal["low","medium","high"]="medium"

class TaskUpdate(BaseModel):
    title:str | None = Field(default=None,min_length=1,max_length=100)
    description:str|None=None
    completed:bool|None=None
    priority: Literal["Low","medium","high"]|None=None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    priority: str

    model_config = ConfigDict(from_attributes=True)
