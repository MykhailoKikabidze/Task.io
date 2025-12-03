import grpc

from proto.task import task_pb2, task_pb2_grpc


class TaskGrpcClient:
    def __init__(self, host="task_service", port=50053):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = task_pb2_grpc.TaskServiceStub(self.channel)

    def get_task(self, task_id):
        req = task_pb2.GetTaskRequest(
            id=task_id
        )

        res = self.stub.GetTask(req)
        return res

    def get_project_tasks(self, project_id):
        req = task_pb2.GetProjectTasksRequest(
            project_id=project_id
        )

        res = self.stub.GetProjectTasks(req)
        return res

    def get_sprint_tasks(self, sprint_id):
        req = task_pb2.GetSprintTasksRequest(
            sprint_id=sprint_id
        )

        res = self.stub.GetSprintTasks(req)
        return res

    def get_epic_tasks(self, epic_id):
        req = task_pb2.GetEpicTasksRequest(
            epic_id=epic_id
        )

        res = self.stub.GetEpicTasks(req)
        return res

    def create_task(
        self,
        title,
        description,
        priority,
        type,
        assigned_to,
        epic_id,
        sprint_id,
        project_id,
        start_date,
        end_date,
    ):
        req = task_pb2.CreateTaskRequest(
            title=title,
            description=description,
            priority=priority,
            type=type,
            assigned_to=assigned_to,
            epic_id=epic_id,
            sprint_id=sprint_id,
            project_id=project_id,
            start_date=start_date,
            end_date=end_date
        )

        res = self.stub.CreateTask(req)
        return res

    def update_task(
        self,
        id,
        title,
        description,
        priority,
        type,
        status,
        assigned_to,
        epic_id,
        sprint_id,
        project_id,
        start_date,
        end_date,
    ):
        req = task_pb2.UpdateTaskRequest(
            id=id,
            title=title,
            description=description,
            priority=priority,
            type=type,
            status=status,
            assigned_to=assigned_to,
            epic_id=epic_id,
            sprint_id=sprint_id,
            project_id=project_id,
            start_date=start_date,
            end_date=end_date
        )

        res = self.stub.UpdateTask(req)
        return res

    def delete_task(self, task_id):
        req = task_pb2.DeleteTaskRequest(
            id=task_id
        )

        res = self.stub.DeleteTask(req)
        return res
