from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends,FastAPI,HTTPException,Query,Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from app import models
from app.database import Base,engine,get_db
from app.schemas import TaskCreate, TaskUpdate, TaskResponse

@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
app = FastAPI(title="Taskflow API",lifespan=lifespan)
DBSession = Annotated[Session, Depends(get_db)]

@app.get("/")
def home():
    return {"message": "Welcome to TaskFlow API"}

@app.get("/health")
def health_check():
    return {"status":"healthy"}

@app.post("/tasks",response_model=TaskResponse,status_code=201)
def create_task(data: TaskCreate, db: DBSession):
    task = models.Task(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.get("/tasks",response_model=list[TaskResponse])
def get_tasks(
    db: DBSession,
    completed:bool|None=None,
    priority:str|None=Query(
        default=None,pattern="^(low|medium|high)$"
    ),
    limit: int=Query(default=10,ge=1,le=100),
    offset:int=Query(default=0,ge=0),

):
    statement = select(models.Task)

    if completed is not None:
        statement = statement.where(
            models.Task.completed == completed
        )

    if priority is not None:
        statement = statement.where(
            models.Task.priority == priority
        )

    statement = statement.order_by(models.Task.id).limit(limit).offset(offset)

    return db.scalars(statement).all()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: DBSession):
    task = db.get(models.Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, db: DBSession):
    task = db.get(models.Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: DBSession):
    task = db.get(models.Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return Response(status_code=204)
