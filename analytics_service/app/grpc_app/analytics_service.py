from concurrent import futures
import grpc

from app.services.analytics import AnalyticsService
from . import analytics_pb2
from . import analytics_pb2_grpc


class AnalyticsServicer(analytics_pb2_grpc.AnalyticsServiceServicer):
    def __init__(self):
        self.analytics_service = AnalyticsService()

    def GetTimelineAll(self, request, context):
        try:
            timeline = self.analytics_service.get_timeline_all(request.user_id)

            return analytics_pb2.TimelineResponse(
                tasks=[
                    analytics_pb2.TaskInfo(
                        task_name=task["task_name"],
                        project_name=task["project_name"],
                        start_date=task["start_date"],
                        end_date=task["end_date"],
                    )
                    for task in timeline
                ]
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Timeline reading failed: {e}")

    def GetTimelineProject(self, request, context):
        try:
            timeline = self.analytics_service.get_timeline_project(request.user_id, request.project_id)

            return analytics_pb2.TimelineResponse(
                tasks=[
                    analytics_pb2.TaskInfo(
                        task_name=task["task_name"],
                        project_name=task["project_name"],
                        start_date=task["start_date"],
                        end_date=task["end_date"],
                    )
                    for task in timeline
                ]
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Timeline reading failed: {e}")

    def GetTimelineAllMine(self, request, context):
        try:
            timeline = self.analytics_service.get_timeline_all_mine(request.user_id)

            return analytics_pb2.TimelineResponse(
                tasks=[
                    analytics_pb2.TaskInfo(
                        task_name=task["task_name"],
                        project_name=task["project_name"],
                        start_date=task["start_date"],
                        end_date=task["end_date"],
                    )
                    for task in timeline
                ]
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Timeline reading failed: {e}")

    def GetTimelineProjectMine(self, request, context):
        try:
            timeline = self.analytics_service.get_timeline_project_mine(request.user_id, request.project_id)

            return analytics_pb2.TimelineResponse(
                tasks=[
                    analytics_pb2.TaskInfo(
                        task_name=task["task_name"],
                        project_name=task["project_name"],
                        start_date=task["start_date"],
                        end_date=task["end_date"],
                    )
                    for task in timeline
                ]
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Timeline reading failed: {e}")

    def GetTasksCompletedByUser(self, request, context):
        tasks_user = self.analytics_service.get_tasks_completed_by_user(request.project_id)

        if tasks_user:
            return analytics_pb2.TasksCompletedByUserResponse(
                user_task=[
                    analytics_pb2.UserTasks(
                        user_id=ut["user_id"],
                        full_name=ut["full_name"],
                        completed_tasks=ut["completed_tasks"],
                    )
                    for ut in tasks_user
                ]
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Tasks completed by user reading failed")
            return analytics_pb2.TasksCompletedByUserResponse()

    def GetTasksStatusInSprints(self, request, context):
        try:
            sprints = self.analytics_service.get_tasks_status_in_sprints(request.project_id)

            return analytics_pb2.TasksStatusInSprintsResponse(
                sprints=[
                    analytics_pb2.SprintInfo(
                        sprint_id=sprint["sprint_id"],
                        name=sprint["name"],
                        completed_tasks=sprint["completed_tasks"],
                        uncompleted_tasks=sprint["uncompleted_tasks"],
                    )
                    for sprint in sprints
                ]
            )

        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Tasks status in sprints reading failed: {e}")

    def GetTasksProgressByDay(self, request, context):
        days = self.analytics_service.get_tasks_progress_by_day(request.project_id)

        if days:
            return analytics_pb2.TasksProgressByDayResponse(
                days=[
                    analytics_pb2.DayInfo(
                        day=day["day"],
                        tasks=day["tasks"],
                    )
                    for day in days
                ]
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("Tasks progress by day reading failed")
            return analytics_pb2.TasksProgressByDayResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    analytics_pb2_grpc.add_AnalyticsServiceServicer_to_server(AnalyticsServicer(), server)
    server.add_insecure_port("[::]:50054")
    return server
