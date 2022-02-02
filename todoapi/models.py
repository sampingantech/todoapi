from sqlmodel import SQLModel, Field


class TodoBase(SQLModel):
    title: str
    is_done: bool


class Todo(TodoBase, table=True):
    id: int = Field(default=None, primary_key=True)


class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    pass