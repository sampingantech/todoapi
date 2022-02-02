from typing import Optional
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate

from todoapi.db import get_session, init_db
from todoapi.models import Todo, TodoCreate

from .config import settings


app = FastAPI(title=settings.app_name, default_response_class=ORJSONResponse)


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


@app.get("/")
def read_root():
    return {"app_name": settings.app_name}


@app.get("/todos", response_model=Page[Todo])
async def get_todos(
    is_done: Optional[bool] = None,
    params: Params = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = select(Todo)
    if is_done is not None:
        query = select(Todo).where(Todo.is_done == is_done)
    return await paginate(session, query, params)


@app.get("/todos/{todo_id}")
async def get_todo(todo_id: int, session: AsyncSession = Depends(get_session)) -> Todo:
    try:
        result = await session.execute(select(Todo).where(Todo.id == todo_id))
        todo = result.scalars().one()
        return todo
    except NoResultFound:
        raise HTTPException(status_code=404)


@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(
    todo_id: int, todo_update: TodoCreate, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalars().one_or_none()
    if not todo:
        raise HTTPException(status_code=404)
    todo.title = todo_update.title
    todo.is_done = todo_update.is_done
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


@app.post("/todos", response_model=Todo)
async def add_todo(todo: TodoCreate, session: AsyncSession = Depends(get_session)):
    todo = Todo(**todo.dict())
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo
