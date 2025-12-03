from fastapi import APIRouter, HTTPException, Path
from fastapi.params import Depends
from models.analytics_models import TaskInfo, UserTasks, SprintInfo, DayInfo
from routers.auth_service import get_current_user
from models.auth_models import User
from clients.grpc.analytics_grpc import AnalyticsGrpcClient

router = APIRouter()


@router.get("/timeline/all", response_model=list[TaskInfo])
def get_all_timeline(current_user: User = Depends(get_current_user)):
    user_id = current_user.user_id
    client = AnalyticsGrpcClient()

    try:
        resp = client.get_all_timeline(user_id)

        return [
            TaskInfo(
                task_name=task.task_name,
                project_name=task.project_name,
                start_date=task.start_date,
                end_date=task.end_date,
            )
            for task in resp.tasks
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline/{project_id}", response_model=list[TaskInfo])
def get_project_timeline(
    project_id: str = Path(..., description="Project UUID"),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.user_id
    client = AnalyticsGrpcClient()

    try:
        resp = client.get_project_timeline(user_id, project_id)

        return [
            TaskInfo(
                task_name=task.task_name,
                project_name=task.project_name,
                start_date=task.start_date,
                end_date=task.end_date,
            )
            for task in resp.tasks
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline/all/me", response_model=list[TaskInfo])
def get_all_mine_timeline(current_user: User = Depends(get_current_user)):
    user_id = current_user.user_id
    client = AnalyticsGrpcClient()

    try:
        resp = client.get_all_mine_timeline(user_id)

        return [
            TaskInfo(
                task_name=task.task_name,
                project_name=task.project_name,
                start_date=task.start_date,
                end_date=task.end_date,
            )
            for task in resp.tasks
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline/me/{project_id}", response_model=list[TaskInfo])
def get_mine_project_timeline(
    project_id: str = Path(..., description="Project UUID"),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.user_id
    client = AnalyticsGrpcClient()

    try:
        resp = client.get_mine_project_timeline(user_id, project_id)

        return [
            TaskInfo(
                task_name=task.task_name,
                project_name=task.project_name,
                start_date=task.start_date,
                end_date=task.end_date,
            )
            for task in resp.tasks
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/completed-by-user/{project_id}", response_model=list[UserTasks])
def get_tasks_completed_by_users(
    project_id: str = Path(..., description="Project UUID"),
    current_user: User = Depends(get_current_user),
):
    client = AnalyticsGrpcClient()

    try:
        resp = client.get_tasks_completed_by_users(project_id)

        return [
            UserTasks(
                user_id=ut.user_id,
                full_name=ut.full_name,
                completed_tasks=ut.completed_tasks,
            )
            for ut in resp.user_task
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sprints/task-status/{project_id}", response_model=list[SprintInfo])
def get_tasks_status_in_sprints(
    project_id: str = Path(..., description="Project UUID"),
    current_user: User = Depends(get_current_user),
):
    client = AnalyticsGrpcClient()

    try:
        resp = client.get_tasks_status_in_sprints(project_id)

        return [
            SprintInfo(
                sprint_id=sprint.sprint_id,
                name=sprint.name,
                completed_tasks=sprint.completed_tasks,
                uncompleted_tasks=sprint.uncompleted_tasks,
            )
            for sprint in resp.sprints
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/progress-by-day/{project_id}", response_model=list[DayInfo])
def get_tasks_progress_by_day(
    project_id: str = Path(..., description="Project UUID"),
    current_user: User = Depends(get_current_user),
):
    client = AnalyticsGrpcClient()

    try:
        resp = client.get_tasks_progress_by_day(project_id)

        return [
            DayInfo(
                day=d.day,
                tasks=d.tasks,
            )
            for d in resp.days
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
