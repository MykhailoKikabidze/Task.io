from pydantic import BaseModel


class RegisterData(BaseModel):
    name: str
    surname: str
    email: str
    password: str
    img_url: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class User(BaseModel):
    user_id: str
    email: str


class UserInfo(User):
    name: str
    surname: str
    img_url: str


class UserUpdateRequest(BaseModel):
    name: str
    surname: str
    password: str


class LoginInput(BaseModel):
    email: str
    password: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    status: int
    message: str


class ImageResponse(BaseModel):
    url: str


class UserOut(BaseModel):
    user_id: str
    name: str
    surname: str
    email: str
