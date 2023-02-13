from typing import List, Optional
from db import async_session_maker, User, Todo
from schemas import TodoBase, TodoInfo, TodoStatusChange, Status
from sqlalchemy.future import select


status = {
    Status.Done: "done",
    Status.Archive: "archive",
    Status.Todo: "todo",
    Status.Inprogress: "in_progress"
}

async def get_todos(user: User) -> List[TodoInfo]:
    todos: List[Todo]
    async with async_session_maker() as session:
        q = select(Todo).where(Todo.user_id==user.email)
        result = await session.execute(q)
        todos = result.scalars().all()
    return [TodoInfo(id=todo.id, title=todo.title, description=todo.description, status=todo.status) for todo in todos]

async def add_todo(todo_base:TodoBase, user: User) -> TodoInfo:
    todo = Todo(title=todo_base.title, description=todo_base.description)
    async with async_session_maker() as session:
        todo.user_id = user.email
        session.add(todo)
        await session.commit()
        await session.refresh(todo)
    return todo

async def update_todo(todo_update: TodoStatusChange, user: User) -> Optional[TodoInfo]:
    todo: Todo
    async with async_session_maker() as session:
        q = select(Todo).where((Todo.id==todo_update.id) & (Todo.user_id==user.email))
        result = await session.execute(q)
        todo = result.scalars().first()
        if todo is not None:
            todo.status = status[todo_update.status]
            session.add(todo)
            await session.commit()
            await session.refresh(todo)
    if todo:
        return TodoInfo(id=todo.id, title=todo.title, description=todo.description, status=todo.status)
    return None