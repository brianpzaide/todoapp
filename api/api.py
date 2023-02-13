from fastapi import Depends, FastAPI, HTTPException
from typing import Dict, List
import todos
from db import User, create_db_and_tables
from schemas import UserCreate, UserRead, TodoBase, TodoInfo, TodoStatusChange
from users import auth_backend, current_active_user, fastapi_users

api = FastAPI()

api.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
)
api.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

@api.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}

@api.get("/todos")
async def get_todos(user: User = Depends(current_active_user)) -> Dict[str, List[TodoInfo]]:
    result: List[TodoInfo] = await todos.get_todos(user)
    return {"todos": result}

@api.post("/todos")
async def add_todo(todo: TodoBase, user: User = Depends(current_active_user)) -> TodoInfo:
    result: TodoInfo = await todos.add_todo(todo_base=todo, user=user)
    return result

@api.put("/todos")
async def set_todo_status(todo: TodoStatusChange, user: User = Depends(current_active_user)) -> TodoInfo:
    result: TodoInfo = await todos.update_todo(todo_update=todo, user=user)
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return result


@api.on_event("startup")
async def on_startup():
    await create_db_and_tables()
