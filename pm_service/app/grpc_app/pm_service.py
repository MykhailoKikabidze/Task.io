from concurrent import futures
import grpc

from app.services.project import ProjectService
from app.services.epic import EpicService
from app.services.sprint import SprintService
from . import pm_pb2
from . import pm_pb2_grpc


class PmServicer(pm_pb2_grpc.ProjectServiceServicer):
    def __init__(self):
        self.project_service = ProjectService()
        self.epic_service = EpicService()
        self.sprint_service = SprintService()

    def CreateProject(self, request, context):

        project = self.project_service.create_project(
            name=request.name,
            description=request.description,
            color=request.color,
            img_url=request.img_url,
            type_project=request.type,
            users=request.users,
        )
        if project:
            return pm_pb2.ProjectResponse(
                id=project["id"],
                name=project["name"],
                description=project["description"],
                color=project["color"],
                img_url=project["img_url"],
                type=project["type"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Project creation failed")
            return pm_pb2.ProjectResponse()

    def GetProject(self, request, context):

        project = self.project_service.get_project(request.project_id)

        if project:
            return pm_pb2.ProjectResponse(
                id=project["id"],
                name=project["name"],
                description=project["description"],
                color=project["color"],
                img_url=project["img_url"],
                type=project["type"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Project reading failed")
            return pm_pb2.ProjectResponse()

    def UpdateProject(self, request, context):

        project = self.project_service.update_project(project_id=request.id, name=request.name,
                                                      description=request.description, color=request.color,
                                                      type_project=request.type)

        if project:
            return pm_pb2.ProjectResponse(
                id=project["id"],
                name=project["name"],
                description=project["description"],
                color=project["color"],
                img_url=project["img_url"],
                type=project["type"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Project update failed")
            return pm_pb2.ProjectResponse()

    def UpdateProjectImg(self, request, context):

        project = self.project_service.update_project_img(project_id=request.id, img_url=request.img_url)

        if project:
            return pm_pb2.ProjectResponse(
                id=project["id"],
                name=project["name"],
                description=project["description"],
                color=project["color"],
                img_url=project["img_url"],
                type=project["type"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Project update failed")
            return pm_pb2.ProjectResponse()

    def UpdateProjectUsers(self, request, context):

        users = [{"id": u.id, "role": u.role} for u in request.users]

        res = self.project_service.update_project_users(project_id=request.id, users=users)

        if res:
            return pm_pb2.UpdateProjectUsersResponse(
                id=res["project_id"],
                users=[
                    pm_pb2.UserRole(
                        id=u["user_id"],
                        role=u["role"]
                    )
                    for u in res["users"]
                ]
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Project users update failed")
            return pm_pb2.UpdateProjectUsersResponse()

    def DeleteProject(self, request, context):

        res = self.project_service.delete_project(project_id=request.id)

        if res:
            return pm_pb2.DeleteProjectResponse(
                status=204,
                message="Project was deleted successfully"
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Project deleting was failed")
            return pm_pb2.DeleteProjectResponse()

    def GetUserProjects(self, request, context):

        res = self.project_service.get_user_projects(user_id=request.user_id)

        if res:
            print(res, flush=True)

            return pm_pb2.UserProjectsResponse(
                projects=[
                    pm_pb2.ProjectResponse(
                        id=item["id"],
                        name=item["name"],
                        description=item["description"],
                        color=item["color"],
                        img_url=item["img_url"],
                        type=item["type"],
                    )
                    for item in res
                ]
            )
        elif not res:
            return pm_pb2.UserProjectsResponse()
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Project not found")
            return pm_pb2.UserProjectsResponse()

    def GetProjectUsers(self, request, context):

        res = self.project_service.get_project_users(project_id=request.project_id)

        if res:
            return pm_pb2.ProjectUsersResponse(
                users=[
                    pm_pb2.UserInfo(
                        user_id=item["user_id"],
                        email=item["email"],
                        name=item["name"],
                        surname=item["surname"],
                        img_url=item["img_url"],
                        role=item["role"]
                    )
                    for item in res
                ]
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Project not found")
            return pm_pb2.ProjectUsersResponse()

    def GetSprint(self, request, context):

        sprint = self.sprint_service.get_sprint(id=request.id)

        if sprint:
            return pm_pb2.SprintResponse(
                id=sprint["id"],
                name=sprint["name"],
                description=sprint["description"],
                start_date=sprint["start_date"],
                end_date=sprint["end_date"],
                is_started=sprint["is_started"],
                project_id=sprint["project_id"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Sprint reading failed")
            return pm_pb2.SprintResponse()

    def GetProjectSprints(self, request, context):

        try:
            project_sprints = self.sprint_service.get_project_sprints(project_id=request.project_id)

            return pm_pb2.ProjectSprintsResponse(
                sprints=[
                    pm_pb2.SprintResponse(
                        id=sprint["id"],
                        name=sprint["name"],
                        description=sprint["description"],
                        start_date=sprint["start_date"],
                        end_date=sprint["end_date"],
                        is_started=sprint["is_started"],
                        project_id=sprint["project_id"],
                    )
                    for sprint in project_sprints
                ]
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Project sprints reading failed: {e}")

    def CreateSprint(self, request, context):
        sprint = self.sprint_service.create_sprint(
            name=request.name,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            is_started=request.is_started,
            project_id=request.project_id,
            tasks=request.tasks
        )

        if sprint:
            return pm_pb2.SprintResponse(
                id=sprint["id"],
                name=sprint["name"],
                description=sprint["description"],
                start_date=sprint["start_date"],
                end_date=sprint["end_date"],
                is_started=sprint["is_started"],
                project_id=sprint["project_id"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Sprint creating failed")
            return pm_pb2.SprintResponse()

    def UpdateSprint(self, request, context):
        sprint = self.sprint_service.update_sprint(
            id=request.id,
            name=request.name,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            is_started=request.is_started,
            project_id=request.project_id,
            tasks=request.tasks
        )

        if sprint:
            return pm_pb2.SprintResponse(
                id=sprint["id"],
                name=sprint["name"],
                description=sprint["description"],
                start_date=sprint["start_date"],
                end_date=sprint["end_date"],
                is_started=sprint["is_started"],
                project_id=sprint["project_id"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Sprint updating failed")
            return pm_pb2.SprintResponse()

    def DeleteSprint(self, request, context):
        res = self.sprint_service.delete_sprint(id=request.id)

        if res:
            return pm_pb2.DeleteSprintResponse(
                status=204, message="Sprint was deleted successfully"
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Sprint deleting failed")
            return pm_pb2.DeleteSprintResponse()

    def GetEpic(self, request, context):
        epic = self.epic_service.get_epic(id=request.id)

        if epic:
            return pm_pb2.EpicResponse(
                id=epic["id"],
                name=epic["name"],
                description=epic["description"],
                priority=epic["priority"],
                start_date=epic["start_date"],
                end_date=epic["end_date"],
                project_id=epic["project_id"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Epic reading failed")
            return pm_pb2.EpicResponse()

    def GetProjectEpics(self, request, context):
        try:
            project_epics = self.epic_service.get_project_epics(project_id=request.project_id)

            return pm_pb2.ProjectEpicsResponse(
                epics=[
                    pm_pb2.EpicResponse(
                        id=epic["id"],
                        name=epic["name"],
                        description=epic["description"],
                        priority=epic["priority"],
                        start_date=epic["start_date"],
                        end_date=epic["end_date"],
                        project_id=epic["project_id"],
                    )
                    for epic in project_epics
                ]
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Project epics reading failed: {e}")

    def CreateEpic(self, request, context):
        epic = self.epic_service.create_epic(
            name=request.name,
            description=request.description,
            priority=request.priority,
            start_date=request.start_date,
            end_date=request.end_date,
            project_id=request.project_id,
            tasks=request.tasks
        )

        if epic:
            return pm_pb2.EpicResponse(
                id=epic["id"],
                name=epic["name"],
                description=epic["description"],
                priority=epic["priority"],
                start_date=epic["start_date"],
                end_date=epic["end_date"],
                project_id=epic["project_id"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Epic creating failed")
            return pm_pb2.EpicResponse()

    def UpdateEpic(self, request, context):
        epic = self.epic_service.update_epic(
            id=request.id,
            name=request.name,
            description=request.description,
            priority=request.priority,
            start_date=request.start_date,
            end_date=request.end_date,
            project_id=request.project_id,
            tasks=request.tasks
        )

        if epic:
            return pm_pb2.EpicResponse(
                id=epic["id"],
                name=epic["name"],
                description=epic["description"],
                priority=epic["priority"],
                start_date=epic["start_date"],
                end_date=epic["end_date"],
                project_id=epic["project_id"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Epic updating failed")
            return pm_pb2.EpicResponse()

    def DeleteEpic(self, request, context):
        res = self.epic_service.delete_epic(id=request.id)

        if res:
            return pm_pb2.DeleteEpicResponse(
                status=204, message="Epic was deleted successfully"
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Epic deleting failed")
            return pm_pb2.DeleteEpicResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pm_pb2_grpc.add_ProjectServiceServicer_to_server(PmServicer(), server)
    server.add_insecure_port('[::]:50052')
    return server
