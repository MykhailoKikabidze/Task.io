import grpc

from proto.analytics import analytics_pb2, analytics_pb2_grpc


class AnalyticsGrpcClient:
    def __init__(self, host="analytics_service", port=50054):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = analytics_pb2_grpc.AnalyticsServiceStub(self.channel)

    def get_all_timeline(self, user_id):
        req = analytics_pb2.GetTimelineAllRequest(user_id=user_id)
        res = self.stub.GetTimelineAll(req)
        return res

    def get_project_timeline(self, user_id, project_id):
        req = analytics_pb2.GetTimelineProjectRequest(user_id=user_id, project_id=project_id)
        res = self.stub.GetTimelineProject(req)
        return res

    def get_all_mine_timeline(self, user_id):
        req = analytics_pb2.GetTimelineAllMineRequest(user_id=user_id)
        res = self.stub.GetTimelineAllMine(req)
        return res

    def get_mine_project_timeline(self, user_id, project_id):
        req = analytics_pb2.GetTimelineProjectMineRequest(user_id=user_id, project_id=project_id)
        res = self.stub.GetTimelineProjectMine(req)
        return res

    def get_tasks_completed_by_users(self, project_id):
        req = analytics_pb2.GetTasksCompletedByUserRequest(project_id=project_id)
        res = self.stub.GetTasksCompletedByUser(req)
        return res

    def get_tasks_status_in_sprints(self, project_id):
        req = analytics_pb2.GetTasksStatusInSprintsRequest(project_id=project_id)
        res = self.stub.GetTasksStatusInSprints(req)
        return res

    def get_tasks_progress_by_day(self, project_id):
        req = analytics_pb2.GetTasksProgressByDayRequest(project_id=project_id)
        res = self.stub.GetTasksProgressByDay(req)
        return res
