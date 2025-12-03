from pydantic import BaseModel


class TaskInfo(BaseModel):
    task_name: str
    project_name: str
    start_date: str
    end_date: str


class UserTasks(BaseModel):
    user_id: str
    full_name: str
    completed_tasks: list[str]


class SprintInfo(BaseModel):
    sprint_id: str
    name: str
    completed_tasks: list[str]
    uncompleted_tasks: list[str]


class DayInfo(BaseModel):
    day: str
    tasks: list[str]
