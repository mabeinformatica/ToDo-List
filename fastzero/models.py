from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


class TodoState(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )


@table_registry.mapped_as_dataclass
class Todo:
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str] = mapped_column(String(length=50))
    description: Mapped[str] = mapped_column()
    state: Mapped[TodoState] = mapped_column(default=TodoState.draft)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    userId: Mapped[int] = mapped_column(ForeignKey('users.id'), default=Any)
