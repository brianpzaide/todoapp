from pathlib import Path
from enum import Enum
from typing import Optional, List
import json

import requests

import typer

__app_name__ = "todo-cli"
__version__ = "0.1.0"

class Status(Enum):
    Todo = 'todo'
    Inprogress = 'in_progress'
    Archive = 'archive'
    Done = "done"


routes = {
    'register': 'http://localhost:8000/auth/register',
    'login': 'http://localhost:8000/auth/login',
    'todos': 'http://localhost:8000/todos',
}

class Todoer():
    """Attaches HTTP Token Authentication to the given Request object."""
    def __init__(self, username, password, access_token=""):
        self.username = username
        self.password = password
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def __call__(self, r):
        r.headers['Authentication'] = f"Bearer {self.access_token}"
        return r
    
    def register(self):
        """Does the user registration"""
        success = False
        resp = requests.post(routes['register'], json={'email': self.username,'password': self.password})
        if resp.status_code == 201:
            success = True
            self.store_cred()
        return success, resp.json()
    
    def login(self):
        """Does the user login"""
        success = False
        resp = requests.post(routes['login'], data={'username': self.username,'password': self.password})
        if resp.status_code == 200:
            self.access_token = resp.json()['access_token']
            self.headers['Authorization'] = f'Bearer {self.access_token}'
            success = True
            self.store_cred()
        return success
    
    def store_cred(self):
        with open("config.json", 'w') as f:
            json.dump({'username': self.username, 'password': self.password, 'access_token': self.access_token}, f)
    
    def add_todo(self, title, description, to_retry=True):
        success = False
        resp = requests.post(routes['todos'], json={'title': title,'description': description}, headers=self.headers)
        if resp.status_code == 200:
            success = True
        if to_retry:
            if resp.status_code == 401 and self.login():
                return self.add_todo(title, description, to_retry=False)
        return success, resp.json()

    def list_todos(self, to_retry=True):
        success = False
        resp = requests.get(routes['todos'], headers=self.headers)
        if resp.status_code == 200:
            success = True
            print(resp.text)
        if to_retry:
            if resp.status_code == 401 and self.login():
                return self.list_todos(to_retry=False)
        return success, resp.json()

    def change_todo_status(self, todo_id, status, to_retry=True):
        success = False
        resp = requests.put(routes['todos'], json={'id': todo_id,'status': status}, headers=self.headers)
        if resp.status_code == 200:
            success = True
        if to_retry:
            if resp.status_code == 401 and self.login():
                return self.change_todo_status(todo_id, status, to_retry=False)
        return success, resp.json()


app = typer.Typer()

# todoer: Todoer

@app.command(name="register")
def register(username: str, password: str) -> None:
    """Does the user registration providing username and password."""
    global todoer
    todoer = Todoer(username=username, password=password)
    success, err = todoer.register()
    if success:
        todoer.login()
        typer.secho(f"successfully logged in as {todoer.username}", fg=typer.colors.GREEN)
    else:
        typer.secho(f"error registering\n {err['detail']}", fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command(name="add")
def add(
    title: str = typer.Argument(...),
    description: str = typer.Argument(...),
) -> None:
    """Add a new to-do with a DESCRIPTION."""
    success, resp = todoer.add_todo(title, description)
    if success:
        typer.secho(f"""to-do: "{title}" was added """, fg=typer.colors.GREEN)
    else:
        typer.secho(f'Adding to-do failed with {resp["detail"]}', fg=typer.colors.RED)
        raise typer.Exit(1)

@app.command(name="list")
def list_all() -> None:
    """List all todos."""
    success, resp = todoer.list_todos()
    if success:
        todos = resp['todos']
        if len(todos) == 0:
            typer.secho(
                "There are no tasks in the to-do list yet", fg=typer.colors.RED
            )
            raise typer.Exit()
        typer.secho("\nto-do list:\n", fg=typer.colors.BLUE, bold=True)
        columns = (
            "ID.  ",
            "| Title  ",
            "| Status  ",
            "| Description  ",
        )
        headers = "".join(columns)
        typer.secho(headers, fg=typer.colors.BLUE, bold=True)
        typer.secho("-" * len(headers), fg=typer.colors.BLUE)
        
        for todo in todos:
            typer.secho(
                f"{todo['id']}{(len(columns[0]) - len(str(todo['id']))) * ' '}"
                f"| {todo['title']}{(len(columns[1]) - len(todo['title']) - 2) * ' '}"
                f"| {todo['status']}{(len(columns[2]) - len(todo['status']) - 2) * ' '}"
                f"| {todo['description']}",
                fg=typer.colors.BLUE,
            )
        typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE)
    else:
        typer.secho(f'Fetching to-dos failed with {resp["detail"]}', fg=typer.colors.RED)
        raise typer.Exit(1)

@app.command(name="status")
def change_status(todo_id: int = typer.Argument(...), todo_status: Status = typer.Argument(...)) -> None:
    """Change a to-do's status by using its TODO_ID."""
    success, resp = todoer.change_todo_status(todo_id, todo_status.value)
    
    if success:
        typer.secho(
            f"""to-do id: {todo_id} title: "{resp['title']}" status: "{resp['status']}". """,
            fg=typer.colors.GREEN,
        )
    else:
        typer.secho(
            f"""Completing to-do # "{todo_id}" failed with "{resp['detail']}" """,
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

def _version_callback(value:bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True, 
    )
) -> None:
    return

if __name__ == "__main__":
    try:
        with open("config.json","r") as f:
            try:
                cred = json.load(f)
                todoer = Todoer(username=cred.get('username'), password=cred.get('password'), access_token=cred.get('access_token'))
            except json.JSONDecodeError:
                print('error reading credentials. please do app init providing username and password')
    except OSError:
         print('username and password not set. To set username and password please do app init providing username and password')
        
    app(prog_name=__app_name__)