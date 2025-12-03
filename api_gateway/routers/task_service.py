from fastapi import APIRouter, HTTPException, Path
from fastapi.params import Depends
from models.task_models import (
    TaskResponse,
    TasksResponse,
    MessageResponse,
    CreateTaskRequest,
    UpdateTaskRequest,
)
from routers.auth_service import get_current_user
from models.auth_models import User
from clients.grpc.task_grpc import TaskGrpcClient
from utils.notifications import notify_task_event, notify_project_participants

router = APIRouter()


@router.get("/task/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str = Path(..., description="Task UUID"),
    current_user: User = Depends(get_current_user),
):
    client = TaskGrpcClient()
    try:
        resp = client.get_task(task_id)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/project/{project_id}", response_model=TasksResponse)
def get_project_tasks(
    project_id: str = Path(..., description="Task UUID"),
    current_user: User = Depends(get_current_user),
):
    client = TaskGrpcClient()
    try:
        resp = client.get_project_tasks(project_id)

        tasks = TasksResponse(
            tasks=[
                TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    priority=task.priority,
                    type=task.type,
                    status=task.status,
                    assigned_to=task.assigned_to,
                    epic_id=task.epic_id,
                    sprint_id=task.sprint_id,
                    project_id=task.project_id,
                    start_date=task.start_date,
                    end_date=task.end_date,
                )
                for task in resp.tasks
            ]
        )
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/sprint/{sprint_id}", response_model=TasksResponse)
def get_sprint_tasks(
    sprint_id: str = Path(..., description="Task UUID"),
    current_user: User = Depends(get_current_user),
):
    client = TaskGrpcClient()
    try:
        resp = client.get_sprint_tasks(sprint_id)

        tasks = TasksResponse(
            tasks=[
                TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    priority=task.priority,
                    type=task.type,
                    status=task.status,
                    assigned_to=task.assigned_to,
                    epic_id=task.epic_id,
                    sprint_id=task.sprint_id,
                    project_id=task.project_id,
                    start_date=task.start_date,
                    end_date=task.end_date,
                )
                for task in resp.tasks
            ]
        )
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/epic/{epic_id}", response_model=TasksResponse)
def get_epic_tasks(
    epic_id: str = Path(..., description="Task UUID"),
    current_user: User = Depends(get_current_user),
):
    client = TaskGrpcClient()
    try:
        resp = client.get_epic_tasks(epic_id)

        tasks = TasksResponse(
            tasks=[
                TaskResponse(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    priority=task.priority,
                    type=task.type,
                    status=task.status,
                    assigned_to=task.assigned_to,
                    epic_id=task.epic_id,
                    sprint_id=task.sprint_id,
                    project_id=task.project_id,
                    start_date=task.start_date,
                    end_date=task.end_date,
                )
                for task in resp.tasks
            ]
        )
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/task", response_model=TaskResponse)
async def create_task(
    task: CreateTaskRequest, current_user: User = Depends(get_current_user)
):
    client = TaskGrpcClient()

    try:
        resp = client.create_task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            type=task.type,
            assigned_to=task.assigned_to,
            epic_id=task.epic_id,
            sprint_id=task.sprint_id,
            project_id=task.project_id,
            start_date=task.start_date,
            end_date=task.end_date,
        )

        await notify_task_event("task_created", resp)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/task", response_model=TaskResponse)
async def update_task(
    task: UpdateTaskRequest, current_user: User = Depends(get_current_user)
):
    client = TaskGrpcClient()

    try:
        resp = client.update_task(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            type=task.type,
            status=task.status,
            assigned_to=task.assigned_to,
            epic_id=task.epic_id,
            sprint_id=task.sprint_id,
            project_id=task.project_id,
            start_date=task.start_date,
            end_date=task.end_date,
        )

        await notify_task_event("task_updated", resp)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/task/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: str = Path(..., description="Task UUID"),
    current_user: User = Depends(get_current_user),
):
    client = TaskGrpcClient()

    try:
        before = client.get_task(task_id)
        resp = client.delete_task(task_id)

        await notify_project_participants(
            project_id=before.project_id,
            event_type="task_deleted",
            payload={"task": {"id": task_id}},
        )
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
