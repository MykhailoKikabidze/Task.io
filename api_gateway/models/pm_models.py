from pydantic import BaseModel


# Projects
class Project(BaseModel):
    name: str
    description: str
    color: str
    img_url: str
    type: str


class UserRole(BaseModel):
    id: str
    role: str


class CreateProjectRequest(Project):
    users: list[UserRole]


class ProjectResponse(Project):
    id: str


class ProjectUsersRequest(BaseModel):
    id: str
    users: list[UserRole]


class ProjectUsersResponse(BaseModel):
    id: str
    users: list[UserRole]


class DeleteProjectResponse(BaseModel):
    status: int
    message: str


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    surname: str
    img_url: str
    role: str


class ProjectUsersResponseExtended(BaseModel):
    users: list[UserInfo]


class UserProjectsResponse(BaseModel):
    projects: list[ProjectResponse]


class UpdateProjectRequest(BaseModel):
    id: str
    name: str
    description: str
    color: str
    type: str


# Sprints
class CreateSprintRequest(BaseModel):
    name: str
    description: str
    start_date: str
    end_date: str = ""
    is_started: bool = False
    project_id: str
    tasks: list[str] = []


class UpdateSprintRequest(CreateSprintRequest):
    id: str


class SprintResponse(BaseModel):
    id: str
    name: str
    description: str
    start_date: str
    end_date: str = ""
    is_started: bool = False
    project_id: str


class SprintsResponse(BaseModel):
    sprints: list[SprintResponse] = []


class DeleteSprintResponse(BaseModel):
    status: int
    message: str


# Epics
class CreateEpicRequest(BaseModel):
    name: str
    description: str
    priority: int
    start_date: str
    end_date: str = ""
    project_id: str
    tasks: list[str] = []


class UpdateEpicRequest(CreateEpicRequest):
    id: str


class EpicResponse(BaseModel):
    id: str
    name: str
    description: str
    priority: int
    start_date: str
    end_date: str = ""
    project_id: str


class EpicsResponse(BaseModel):
    epics: list[EpicResponse] = []


class DeleteEpicResponse(BaseModel):
    status: int
    message: str
