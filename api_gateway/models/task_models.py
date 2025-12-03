from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    title: str
    description: str
    priority: int
    type: str
    assigned_to: str = ""
    epic_id: str = ""
    sprint_id: str = ""
    project_id: str
    start_date: str
    end_date: str = ""


class UpdateTaskRequest(CreateTaskRequest):
    id: str
    status: str


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: int
    type: str
    status: str
    assigned_to: str | None
    epic_id: str | None
    sprint_id: str | None
    project_id: str
    start_date: str
    end_date: str | None


class TasksResponse(BaseModel):
    tasks: list[TaskResponse] = []


class MessageResponse(BaseModel):
    status: int
    message: str
