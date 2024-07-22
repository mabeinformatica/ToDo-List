from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastzero.database import get_session
from fastzero.models import Todo, TodoState, User
from fastzero.schemas import (
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fastzero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

TodoSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
def create_todo(todo: TodoSchema, session: TodoSession, user: CurrentUser):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        userId=user.id,
    )

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
def list_todos(  # noqa: PLR0913, PLR0917
    session: TodoSession,
    user: CurrentUser,
    title: str | None = None,
    description: str | None = None,
    state: TodoState | None = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(Todo).where(Todo.userId == user.id)

    if title:
        query = query.filter(Todo.title.ilike(f'%{title}%'))

    if description:
        query = query.filter(Todo.description.ilike(f'%{description}%'))

    if state:
        query = query.filter(Todo.state == state)

    todos = session.scalars(query.offset(skip).limit(limit)).all()

    return {'todos': todos}


@router.delete('/{todo_id}', response_model=Message)
def delete_todo(
    todo_id: int,
    session: TodoSession,
    current_user: CurrentUser,
):
    todo = session.scalar(
        select(Todo).where(Todo.userId == current_user.id, Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    session.delete(todo)
    session.commit()

    return {'message': 'Task has been deleted'}


@router.patch('/{todo_id}', response_model=TodoPublic)
def update_partial_todo(
    todo_id: int,
    session: TodoSession,
    current_user: CurrentUser,
    todo: TodoUpdate,
):
    db_todo = session.scalar(
        select(Todo).where(Todo.userId == current_user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found',
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
