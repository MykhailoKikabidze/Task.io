import grpc

from proto.auth import auth_pb2, auth_pb2_grpc


class AuthGrpcClient:
    def __init__(self, host="auth_service", port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    def create_user(self, name, surname, email, password, img_url):
        request = auth_pb2.CreateUserRequest(
            name=name,
            surname=surname,
            email=email,
            password=password,
            img_url=img_url
        )
        response = self.stub.CreateUser(request)
        return response

    def login_user(self, email, password):
        request = auth_pb2.LoginUserRequest(
            email=email,
            password=password
        )
        response = self.stub.LoginUser(request)
        return response

    def get_user_by_id(self, uuid):
        request = auth_pb2.GetUserRequest(
            user_id=uuid
        )
        response = self.stub.GetUser(request)
        return response

    def update_user(self, name, surname, email, password):
        request = auth_pb2.UpdateUserRequest(
            name=name,
            surname=surname,
            email=email,
            password=password
        )
        response = self.stub.UpdateUser(request)
        return response

    def update_user_img(self, email, img_url):
        request = auth_pb2.UpdateUserImageRequest(
            email=email,
            img_url=img_url
        )
        response = self.stub.UpdateUserImage(request)
        return response

    def delete_user(self, email):
        request = auth_pb2.DeleteUserRequest(
            email=email
        )
        response = self.stub.DeleteUser(request)
        return response

    def search_users(self, substr: str):
        request = auth_pb2.SearchUsersRequest(
            substr=substr
        )
        response = self.stub.SearchUsers(request)
        return response

    def init_db(self, num):
        request = auth_pb2.InitDBRequest(
            num=num
        )
        response = self.stub.InitDB(request)
        return response
