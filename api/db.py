from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, orm
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTableUUID,
)

DATABASE_URL = "sqlite+aiosqlite:///./todos.db"
Base: DeclarativeMeta = declarative_base()

class User(SQLAlchemyBaseUserTableUUID, Base):
    todos = orm.relationship("Todo", back_populates="user")


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):  
    pass

class Todo(Base):
    """Todo model representing a todo table."""

    __tablename__ = "todo"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(String(255))
    status = Column(Enum("todo", "in_progress", "archive", "done"), unique=False, default="todo")
    user_id = Column(String, ForeignKey("user.email"))
    user = orm.relationship("User", back_populates="todos")

    def __repr__(self):
        return f"Todo(id={self.id}, title={self.title}, description={self.description}, year={self.status})"

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_access_token_db(session: AsyncSession = Depends(get_async_session)):  
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)