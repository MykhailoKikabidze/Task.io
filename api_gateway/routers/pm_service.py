from fastapi import APIRouter, HTTPException, File, UploadFile, Path
from fastapi.params import Depends

import os
from uuid import uuid4
from clients.minio_client import upload_file

from clients.grpc.pm_grpc import PmGrpcClient
from config import get_settings, Settings
from routers.auth_service import get_current_user
from models.auth_models import User
from models.pm_models import (
    ProjectResponse,
    CreateProjectRequest,
    ProjectUsersResponse,
    DeleteProjectResponse,
    ProjectUsersResponseExtended,
    UserProjectsResponse,
    UpdateProjectRequest,
    ProjectUsersRequest,
    UserInfo,
    SprintResponse,
    SprintsResponse,
    DeleteSprintResponse,
    UpdateSprintRequest,
    CreateSprintRequest,
    EpicResponse,
    EpicsResponse,
    DeleteEpicResponse,
    UpdateEpicRequest,
    CreateEpicRequest,
)
from utils.notifications import (
    notify_project_participants,
    notify_project_user_changes,
    notify_sprint_event,
    notify_epic_event,
)
from websockets.manager import manager as ws_manager

router = APIRouter()


@router.post("/project", response_model=ProjectResponse, tags=["project"])
async def create_project(
    project: CreateProjectRequest, current_user: User = Depends(get_current_user)
):
    client = PmGrpcClient()

    try:
        resp = client.create_project(
            name=project.name,
            description=project.description,
            color=project.color,
            img_url=project.img_url,
            type=project.type,
            users=project.users,
        )

        await notify_project_participants(
            project_id=resp.id,
            event_type="project_created",
            payload={"name": resp.name},
        )
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project", response_model=ProjectResponse, tags=["project"])
def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    client = PmGrpcClient()

    try:
        resp = client.get_project(project_id)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/project", response_model=ProjectResponse, tags=["project"])
async def update_project(
    project: UpdateProjectRequest, current_user: User = Depends(get_current_user)
):
    client = PmGrpcClient()

    try:
        resp = client.update_project(
            project_id=project.id,
            name=project.name,
            description=project.description,
            color=project.color,
            type=project.type,
        )

        await notify_project_participants(
            project_id=resp.id,
            event_type="project_updated",
            payload={
                "fields": {
                    "name": resp.name,
                    "description": resp.description,
                    "color": resp.color,
                    "type": resp.type,
                }
            },
        )

        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/project/img/{project_id}", response_model=ProjectResponse, tags=["project"]
)
async def update_project_img(
    project_id: str = Path(..., description="Project UUID"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    client = PmGrpcClient()
    try:
        ext = os.path.splitext(file.filename)[1]
        file_name = f"{project_id}_{uuid4().hex}{ext}"
        url = upload_file(
            bucket_name="project-avatars",
            file_data=file.file,
            file_name=file_name,
            content_type=file.content_type,
        )
        resp = client.update_project_img(project_id=project_id, img_url=url)
        if not resp:
            raise HTTPException(status_code=401, detail="Invalid project ID")

        await notify_project_participants(
            project_id=project_id,
            event_type="project_image_updated",
            payload={"img_url": url},
        )

        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/project/users", response_model=ProjectUsersResponse, tags=["project"])
async def update_project_users(
    req: ProjectUsersRequest, current_user: User = Depends(get_current_user)
):
    client = PmGrpcClient()
    try:
        old_resp = client.get_project_users(project_id=req.id)
        old_users = [u.user_id for u in old_resp.users]

        resp = client.update_project_users(project_id=req.id, users=req.users)
        new_users = [u.id for u in resp.users]

        await notify_project_user_changes(
            project_id=req.id, old_users=old_users, new_users=new_users
        )

        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/project", response_model=DeleteProjectResponse, tags=["project"])
async def delete_project(
    project_id: str, current_user: User = Depends(get_current_user)
):
    client = PmGrpcClient()
    try:
        pu = get_project_users(project_id=project_id)
        user_ids = [u.id for u in pu.users]
        resp = client.delete_project(project_id=project_id)

        for uid in user_ids:
            await ws_manager.send_personal_json(
                uid, {"type": "project_deleted", "project_id": project_id}
            )

        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/project/users", response_model=ProjectUsersResponseExtended, tags=["project"]
)
def get_project_users(project_id: str, current_user: User = Depends(get_current_user)):
    client = PmGrpcClient()
    try:
        resp = client.get_project_users(project_id=project_id)

        users = ProjectUsersResponseExtended(
            users=[
                UserInfo(
                    id=u.user_id,
                    email=u.email,
                    name=u.name,
                    surname=u.surname,
                    img_url=u.img_url,
                    role=u.role,
                )
                for u in resp.users
            ]
        )
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/projects", response_model=UserProjectsResponse, tags=["project"])
def get_user_projects(current_user: User = Depends(get_current_user)):
    client = PmGrpcClient()
    try:
        resp = client.get_user_projects(user_id=current_user.user_id)

        projects = UserProjectsResponse(
            projects=[
                ProjectResponse(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    color=p.color,
                    img_url=p.img_url,
                    type=p.type,
                )
                for p in resp.projects
            ]
        )

        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sprint/{sprint_id}", response_model=SprintResponse, tags=["sprint"])
def get_sprint(
    sprint_id: str = Path(..., description="Sprint UUID"),
    current_user: User = Depends(get_current_user),
):
    client = PmGrpcClient()
    try:
        resp = client.get_sprint(id=sprint_id)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sprint/project/{project_id}", response_model=SprintsResponse, tags=["sprint"]
)
def get_project_sprints(
    project_id: str = Path(..., description="Project UUID"),
    current_user: User = Depends(get_current_user),
):
    client = PmGrpcClient()
    try:
        resp = client.get_project_sprints(project_id=project_id)

        return SprintsResponse(
            sprints=[
                SprintResponse(
                    id=sprint.id,
                    name=sprint.name,
                    description=sprint.description,
                    start_date=sprint.start_date,
                    end_date=sprint.end_date,
                    is_started=sprint.is_started,
                    project_id=sprint.project_id,
                )
                for sprint in resp.sprints
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sprint", response_model=SprintResponse, tags=["sprint"])
async def create_sprint(
    sprint: CreateSprintRequest, current_user: User = Depends(get_current_user)
):
    client = PmGrpcClient()
    try:
        resp = client.create_sprint(
            name=sprint.name,
            description=sprint.description,
            start_date=sprint.start_date,
            end_date=sprint.end_date,
            is_started=sprint.is_started,
            project_id=sprint.project_id,
            tasks=sprint.tasks,
        )

        await notify_sprint_event("sprint_created", resp)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sprint", response_model=SprintResponse, tags=["sprint"])
async def update_sprint(
    sprint: UpdateSprintRequest, current_user: User = Depends(get_current_user)
):
    client = PmGrpcClient()
    try:
        resp = client.update_sprint(
            id=sprint.id,
            name=sprint.name,
            description=sprint.description,
            start_date=sprint.start_date,
            end_date=sprint.end_date,
            is_started=sprint.is_started,
            project_id=sprint.project_id,
            tasks=sprint.tasks,
        )

        await notify_sprint_event("sprint_updated", resp)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/sprint/{sprint_id}", response_model=DeleteSprintResponse, tags=["sprint"]
)
async def delete_sprint(
    sprint_id: str = Path(..., description="Sprint UUID"),
    current_user: User = Depends(get_current_user),
):
    client = PmGrpcClient()
    try:
        before = client.get_sprint(id=sprint_id)
        resp = client.delete_sprint(id=sprint_id)

        await notify_project_participants(
            project_id=before.project_id,
            event_type="sprint_deleted",
            payload={"sprint": {"id": sprint_id}},
        )
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/epic/{epic_id}", response_model=EpicResponse, tags=["epic"])
def get_epic(
    epic_id: str = Path(..., description="Epic UUID"),
    current_user: User = Depends(get_current_user),
):
    client = PmGrpcClient()
    try:
        resp = client.get_epic(id=epic_id)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/epic/project/{project_id}", response_model=EpicsResponse, tags=["epic"])
def get_project_epics(
    project_id: str = Path(..., description="Project UUID"),
    current_user: User = Depends(get_current_user),
):
    client = PmGrpcClient()
    try:
        resp = client.get_project_epics(project_id=project_id)

        return EpicsResponse(
            epics=[
                EpicResponse(
                    id=epic.id,
                    name=epic.name,
                    description=epic.description,
                    priority=epic.priority,
                    start_date=epic.start_date,
                    end_date=epic.end_date,
                    project_id=epic.project_id,
                )
                for epic in resp.epics
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/epic", response_model=EpicResponse, tags=["epic"])
async def create_epic(
    epic: CreateEpicRequest, current_user: User = Depends(get_current_user)
):
    client = PmGrpcClient()
    try:
        resp = client.create_epic(
            name=epic.name,
            description=epic.description,
            priority=epic.priority,
            start_date=epic.start_date,
            end_date=epic.end_date,
            project_id=epic.project_id,
            tasks=epic.tasks,
        )

        await notify_epic_event("epic_created", resp)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/epic", response_model=EpicResponse, tags=["epic"])
async def update_epic(
    epic: UpdateEpicRequest, current_user: User = Depends(get_current_user)
):
    client = PmGrpcClient()
    try:
        resp = client.update_epic(
            id=epic.id,
            name=epic.name,
            description=epic.description,
            priority=epic.priority,
            start_date=epic.start_date,
            end_date=epic.end_date,
            project_id=epic.project_id,
            tasks=epic.tasks,
        )

        await notify_epic_event("epic_updated", resp)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/epic/{epic_id}", response_model=DeleteEpicResponse, tags=["epic"])
async def delete_epic(
    epic_id: str = Path(..., description="Epic UUID"),
    current_user: User = Depends(get_current_user),
):
    client = PmGrpcClient()
    try:
        before = client.get_epic(id=epic_id)
        resp = client.delete_epic(id=epic_id)

        await notify_project_participants(
            project_id=before.project_id,
            event_type="epic_deleted",
            payload={"epic": {"id": epic_id}},
        )
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
