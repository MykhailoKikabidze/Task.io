import grpc

from models.pm_models import CreateSprintRequest
from proto.pm import pm_pb2, pm_pb2_grpc


class PmGrpcClient:
    def __init__(self, host="pm_service", port=50052):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = pm_pb2_grpc.ProjectServiceStub(self.channel)

    def create_project(self, name, description, color, img_url, type, users):

        users_ready = list()

        for user in users:
            user_ready = pm_pb2.UserRole(id=user.id, role=user.role)

            users_ready.append(user_ready)

        req = pm_pb2.CreateProjectRequest(
            name=name,
            description=description,
            color=color,
            img_url=img_url,
            type=type,
            users=users_ready,
        )
        res = self.stub.CreateProject(req)
        return res

    def get_project(self, project_id):
        req = pm_pb2.GetProjectRequest(project_id=project_id)
        res = self.stub.GetProject(req)
        return res

    def update_project(self, project_id, name, description, color, type):
        req = pm_pb2.UpdateProjectRequest(
            id=project_id, name=name, description=description, color=color, type=type
        )
        res = self.stub.UpdateProject(req)
        return res

    def update_project_img(self, project_id, img_url):
        req = pm_pb2.UpdateProjectImgRequest(id=project_id, img_url=img_url)
        res = self.stub.UpdateProjectImg(req)
        return res

    def update_project_users(self, project_id, users):
        users_grpc = []

        for u in users:
            users_grpc.append(pm_pb2.UserRole(id=u.id, role=u.role))

        req = pm_pb2.UpdateProjectUsersRequest(id=project_id, users=users_grpc)
        res = self.stub.UpdateProjectUsers(req)
        return res

    def delete_project(self, project_id):
        req = pm_pb2.DeleteProjectRequest(id=project_id)
        res = self.stub.DeleteProject(req)
        return res

    def get_project_users(self, project_id):
        req = pm_pb2.GetProjectUsersRequest(project_id=project_id)
        res = self.stub.GetProjectUsers(req)
        return res

    def get_user_projects(self, user_id):
        req = pm_pb2.GetUserProjectsRequest(user_id=user_id)
        res = self.stub.GetUserProjects(req)
        return res

    def get_sprint(self, id):
        req = pm_pb2.GetSprintRequest(id=id)
        res = self.stub.GetSprint(req)
        return res

    def get_project_sprints(self, project_id):
        req = pm_pb2.GetProjectSprintsRequest(project_id=project_id)
        res = self.stub.GetProjectSprints(req)
        return res

    def create_sprint(
        self, name, description, start_date, end_date, is_started, project_id, tasks
    ):
        req = pm_pb2.CreateSprintRequest(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            is_started=is_started,
            project_id=project_id,
            tasks=tasks,
        )
        res = self.stub.CreateSprint(req)
        return res

    def update_sprint(
        self, id, name, description, start_date, end_date, is_started, project_id, tasks
    ):
        req = pm_pb2.UpdateSprintRequest(
            id=id,
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            is_started=is_started,
            project_id=project_id,
            tasks=tasks,
        )
        res = self.stub.UpdateSprint(req)
        return res

    def delete_sprint(self, id):
        req = pm_pb2.DeleteSprintRequest(id=id)
        res = self.stub.DeleteSprint(req)
        return res

    def get_epic(self, id):
        req = pm_pb2.GetEpicRequest(id=id)
        res = self.stub.GetEpic(req)
        return res

    def get_project_epics(self, project_id):
        req = pm_pb2.GetProjectEpicsRequest(project_id=project_id)
        res = self.stub.GetProjectEpics(req)
        return res

    def create_epic(
        self, name, description, priority, start_date, end_date, project_id, tasks
    ):
        req = pm_pb2.CreateEpicRequest(
            name=name,
            description=description,
            priority=priority,
            start_date=start_date,
            end_date=end_date,
            project_id=project_id,
            tasks=tasks,
        )
        res = self.stub.CreateEpic(req)
        return res

    def update_epic(
        self, id, name, description, priority, start_date, end_date, project_id, tasks
    ):
        req = pm_pb2.UpdateEpicRequest(
            id=id,
            name=name,
            description=description,
            priority=priority,
            start_date=start_date,
            end_date=end_date,
            project_id=project_id,
            tasks=tasks,
        )
        res = self.stub.UpdateEpic(req)
        return res

    def delete_epic(self, id):
        req = pm_pb2.DeleteEpicRequest(id=id)
        res = self.stub.DeleteEpic(req)
        return res
