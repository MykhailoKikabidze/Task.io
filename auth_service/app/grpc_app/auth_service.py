from concurrent import futures
import grpc
from app.services.auth import AuthService
from . import auth_pb2
from . import auth_pb2_grpc


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self):
        self.auth_service = AuthService()

    def CreateUser(self, request, context):
        user = self.auth_service.get_user_by_email(email=request.email)
        if user:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("User with this email already exists")
            return auth_pb2.UserResponse()

        user = self.auth_service.create_user(
            name=request.name,
            surname=request.surname,
            email=request.email,
            password=request.password,
            img_url=request.img_url or None
        )
        if user:
            return auth_pb2.UserResponse(
                message="User created successfully",
                user_id=str(user.id),
                email=user.email,
                name=user.name,
                surname=user.surname,
                img_url=user.img_url
            )
        else:
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details("User creation failed")
            return auth_pb2.UserResponse()

    def LoginUser(self, request, context):
        user = self.auth_service.login_user(
            email=request.email,
            password=request.password
        )
        if user:
            return auth_pb2.UserResponse(
                message="Login successful",
                user_id=str(user.id),
                email=user.email,
                name=user.name,
                surname=user.surname,
                img_url=user.img_url
            )
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        context.set_details("Invalid credentials")
        return auth_pb2.UserResponse()

    def GetUser(self, request, context):
        user = self.auth_service.get_user_by_id(request.user_id)
        if user:
            return auth_pb2.UserResponse(
                message="Getting user successful",
                user_id=str(user.id),
                email=user.email,
                name=user.name,
                surname=user.surname,
                img_url=user.img_url
            )
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        context.set_details("Invalid credentials or user is not found")
        return auth_pb2.UserResponse()

    def UpdateUser(self, request, context):
        user = self.auth_service.update_user(name=request.name, surname=request.surname, email=request.email, password=request.password)
        if user:
            return auth_pb2.UserResponse(
                message="Updating user successful",
                user_id=str(user.id),
                email=user.email,
                name=user.name,
                surname=user.surname,
                img_url=user.img_url
            )
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        context.set_details("Invalid credentials or user is not found")
        return auth_pb2.UserResponse()

    def UpdateUserImage(self, request, context):
        user = self.auth_service.update_user_img_url(email=request.email, img_url=request.img_url)
        if user:
            return auth_pb2.UserResponse(
                message="Updating user image successful",
                user_id=str(user.id),
                email=user.email,
                name=user.name,
                surname=user.surname,
                img_url=user.img_url
            )
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        context.set_details("Invalid credentials or user is not found")
        return auth_pb2.UserResponse()

    def DeleteUser(self, request, context):
        response = self.auth_service.delete_user(email=request.email)
        if response:
            return auth_pb2.MessageResponse(
                status=204,
                message="User was deleted successfully"
            )
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        context.set_details("Invalid credentials or user is not found")
        return auth_pb2.MessageResponse()

    def SearchUsers(self, request, context):
        users = self.auth_service.search_users(request.substr)
        resp = auth_pb2.SearchUsersResponse()
        for u in users:
            resp.users.add(
                user_id=str(u.id),
                name=u.name,
                surname=u.surname,
                email=u.email
            )
        return resp

    def InitDB(self, request, context):
        if request.num == 200:
            self.auth_service.init_db()
            return auth_pb2.InitDBResponse(status=200)
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        context.set_details("Invalid credentials or user is not found")
        return auth_pb2.InitDBResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServicer(), server)
    server.add_insecure_port('[::]:50051')
    return server
