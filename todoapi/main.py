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


app = FastAPI()
v1 = FastAPI(title=settings.app_name, default_response_class=ORJSONResponse)


@app.on_event("startup")
async def on_startup():
    await init_db()


@v1.get("/")
def read_root():
    return {"app_name": settings.app_name}


@v1.get("/ping")
async def pong():
    return {"ping": "pong!"}


@v1.get("/todos", response_model=Page[Todo])
async def get_todos(
    is_done: Optional[bool] = None,
    params: Params = Depends(),
    session: AsyncSession = Depends(get_session),
):
    query = select(Todo)
    if is_done is not None:
        query = select(Todo).where(Todo.is_done == is_done)
    return await paginate(session, query, params)


@v1.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int, session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(select(Todo).where(Todo.id == todo_id))
        todo = result.scalars().one()
        return todo
    except NoResultFound:
        raise HTTPException(status_code=404)


@v1.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(
    todo_id: int, todo_update: TodoCreate, session: AsyncSession = Depends(get_session)
):
    #  get object
    result = await session.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalars().one_or_none()
    # err handling not found
    if not todo:
        raise HTTPException(status_code=404)

    # process update
    todo.title = todo_update.title
    todo.is_done = todo_update.is_done
    session.add(todo)

    # commit transaction
    await session.commit()
    await session.refresh(todo)
    return todo


@v1.post("/todos", response_model=Todo)
async def add_todo(todo: TodoCreate, session: AsyncSession = Depends(get_session)):
    todo = Todo(**todo.dict())

    # insert table
    session.add(todo)

    await session.commit()

    # update field
    await session.refresh(todo)
    return todo


app.mount("/v1", v1)
