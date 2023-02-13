# todoapp
This is a todo app, made with FastAPI, FastAPIUsers, Typer, SQLAlchemy.

It contains two parts:
* api which is a todo server.
* ui which is cli for interacting with the api server.

A task can have any `1` of `4` states:
* todo
* in_progress
* done
* archived

Task contains: Title, Description, and what the current status is.

A task can be archived and moved between statuses.

The endpoint for tasks only displays tasks for those users who have authenticated and are authorized to view their tasks.

The commands for the cli are:
* register: to register a user
* add: to add a task (by default task has a status of "todo")
* list: list all the tasks
* status: to change task status