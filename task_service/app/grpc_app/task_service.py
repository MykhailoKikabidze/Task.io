from concurrent import futures
import grpc

from app.services.task import TaskService
from . import task_pb2
from . import task_pb2_grpc


class TaskServicer(task_pb2_grpc.TaskServiceServicer):
    def __init__(self):
        self.task_service = TaskService()

    def GetTask(self, request, context):

        task = self.task_service.get_task(request.id)

        if task:
            return task_pb2.TaskResponse(
                id=task["id"],
                title=task["title"],
                description=task["description"],
                priority=task["priority"],
                type=task["type"],
                status=task["status"],
                assigned_to=task["assigned_to"],
                epic_id=task["epic_id"],
                sprint_id=task["sprint_id"],
                project_id=task["project_id"],
                start_date=task["start_date"],
                end_date=task["end_date"],
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Task reading failed")
            return task_pb2.TaskResponse()

    def GetProjectTasks(self, request, context):
        try:
            project_tasks = self.task_service.get_project_tasks(request.project_id)

            return task_pb2.TasksResponse(
                tasks=[
                    task_pb2.TaskResponse(
                        id=task["id"],
                        title=task["title"],
                        description=task["description"],
                        priority=task["priority"],
                        type=task["type"],
                        status=task["status"],
                        assigned_to=task["assigned_to"],
                        epic_id=task["epic_id"],
                        sprint_id=task["sprint_id"],
                        project_id=task["project_id"],
                        start_date=task["start_date"],
                        end_date=task["end_date"],
                    )
                    for task in project_tasks
                ]
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Project tasks reading failed: {e}")

    def GetSprintTasks(self, request, context):

        try:
            sprint_tasks = self.task_service.get_sprint_tasks(request.sprint_id)

            return task_pb2.TasksResponse(
                tasks=[
                    task_pb2.TaskResponse(
                        id=task["id"],
                        title=task["title"],
                        description=task["description"],
                        priority=task["priority"],
                        type=task["type"],
                        status=task["status"],
                        assigned_to=task["assigned_to"],
                        epic_id=task["epic_id"],
                        sprint_id=task["sprint_id"],
                        project_id=task["project_id"],
                        start_date=task["start_date"],
                        end_date=task["end_date"],
                    )
                    for task in sprint_tasks
                ]
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Sprint tasks reading failed: {e}")

    def GetEpicTasks(self, request, context):
        try:
            epic_tasks = self.task_service.get_epic_tasks(request.epic_id)

            return task_pb2.TasksResponse(
                tasks=[
                    task_pb2.TaskResponse(
                        id=task["id"],
                        title=task["title"],
                        description=task["description"],
                        priority=task["priority"],
                        type=task["type"],
                        status=task["status"],
                        assigned_to=task["assigned_to"],
                        epic_id=task["epic_id"],
                        sprint_id=task["sprint_id"],
                        project_id=task["project_id"],
                        start_date=task["start_date"],
                        end_date=task["end_date"],
                    )
                    for task in epic_tasks
                ]
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Epic tasks reading failed: {e}")

    def CreateTask(self, request, context):
        task = self.task_service.create_task(
            title=request.title,
            description=request.description,
            priority=request.priority,
            type=request.type,
            assigned_to=request.assigned_to,
            epic_id=request.epic_id,
            sprint_id=request.sprint_id,
            project_id=request.project_id,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        if task:
            return task_pb2.TaskResponse(
                id=task["id"],
                title=task["title"],
                description=task["description"],
                priority=task["priority"],
                type=task["type"],
                status=task["status"],
                assigned_to=task["assigned_to"],
                epic_id=task["epic_id"],
                sprint_id=task["sprint_id"],
                project_id=task["project_id"],
                start_date=task["start_date"],
                end_date=task["end_date"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Task creating failed")
            return task_pb2.TaskResponse()

    def UpdateTask(self, request, context):
        task = self.task_service.update_task(
            id=request.id,
            title=request.title,
            description=request.description,
            priority=request.priority,
            type=request.type,
            status=request.status,
            assigned_to=request.assigned_to,
            epic_id=request.epic_id,
            sprint_id=request.sprint_id,
            project_id=request.project_id,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        if task:
            return task_pb2.TaskResponse(
                id=task["id"],
                title=task["title"],
                description=task["description"],
                priority=task["priority"],
                type=task["type"],
                status=task["status"],
                assigned_to=task["assigned_to"],
                epic_id=task["epic_id"],
                sprint_id=task["sprint_id"],
                project_id=task["project_id"],
                start_date=task["start_date"],
                end_date=task["end_date"],
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Task updating failed")
            return task_pb2.TaskResponse()

    def DeleteTask(self, request, context):
        res = self.task_service.delete_task(request.id)

        if res:
            return task_pb2.DeleteTaskResponse(
                status=204, message="Task was deleted successfully"
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Task deleting failed")
            return task_pb2.DeleteTaskResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    task_pb2_grpc.add_TaskServiceServicer_to_server(TaskServicer(), server)
    server.add_insecure_port("[::]:50053")
    return server
