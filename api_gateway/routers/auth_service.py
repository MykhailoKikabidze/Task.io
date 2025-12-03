from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Form,
    Response,
    Request,
    File,
    UploadFile,
    Path,
)
from models.auth_models import (
    RegisterData,
    User,
    TokenPair,
    LoginInput,
    UserInfo,
    UserUpdateRequest,
    TokenRefreshResponse,
    MessageResponse,
    ImageResponse,
    UserOut,
)
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from config import get_settings, Settings
from clients.grpc.auth_grpc import AuthGrpcClient
from clients.minio_client import upload_file
from clients.redis_client import redis_client
from uuid import uuid4
import os
from typing import List

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/form-login")


def create_access_token(
    data: dict,
    secret_key: str,
    algo: str,
    expires_delta: int,
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algo)


def get_current_user(
    token: str = Depends(oauth2_scheme), settings: Settings = Depends(get_settings)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        email = payload.get("email")
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        return User(user_id=user_id, email=email)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/init-db")
def init_db():
    client = AuthGrpcClient()
    try:
        response = client.init_db(200)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register", response_model=UserInfo)
def register(data: RegisterData):
    client = AuthGrpcClient()
    try:
        response = client.create_user(
            name=data.name,
            surname=data.surname,
            email=data.email,
            password=data.password,
            img_url=data.img_url,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=TokenPair)
def login(
    data: LoginInput, response: Response, settings: Settings = Depends(get_settings)
):
    client = AuthGrpcClient()
    try:
        grpc_user = client.login_user(data.email, data.password)

        if not grpc_user.user_id:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        jti = str(uuid4())

        access_token = create_access_token(
            data={"sub": grpc_user.user_id, "email": grpc_user.email},
            secret_key=settings.JWT_SECRET,
            algo=settings.JWT_ALGORITHM,
            expires_delta=settings.ACCESS_TOKEN_EXPIRE,
        )
        refresh_token = create_access_token(
            data={"sub": grpc_user.user_id, "email": grpc_user.email, "jti": jti},
            secret_key=settings.JWT_SECRET,
            algo=settings.JWT_ALGORITHM,
            expires_delta=settings.REFRESH_TOKEN_EXPIRE,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="strict",
            # True in prod
            secure=False,
            max_age=settings.REFRESH_TOKEN_EXPIRE,
        )

        return TokenPair(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response,
    settings: Settings = Depends(get_settings),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token not found")

    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        jti = payload.get("jti")
        if jti:
            redis_client.setex(f"bl:{jti}", settings.REFRESH_TOKEN_EXPIRE, "true")

    except JWTError:
        pass

    response.delete_cookie("refresh_token", httponly=True, samesite="strict")

    return MessageResponse(status=200, message="Successfully logged out")


@router.post("/form-login", include_in_schema=False)
def login_form(
    response: Response,
    username: str = Form(),
    password: str = Form(),
    settings: Settings = Depends(get_settings),
):
    client = AuthGrpcClient()
    try:
        grpc_user = client.login_user(username, password)

        if not grpc_user.user_id:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        jti = str(uuid4())

        access_token = create_access_token(
            data={"sub": grpc_user.user_id, "email": grpc_user.email},
            secret_key=settings.JWT_SECRET,
            algo=settings.JWT_ALGORITHM,
            expires_delta=settings.ACCESS_TOKEN_EXPIRE,
        )
        refresh_token = create_access_token(
            data={"sub": grpc_user.user_id, "email": grpc_user.email, "jti": jti},
            secret_key=settings.JWT_SECRET,
            algo=settings.JWT_ALGORITHM,
            expires_delta=settings.REFRESH_TOKEN_EXPIRE,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="strict",
            # True in prod
            secure=False,
            max_age=settings.REFRESH_TOKEN_EXPIRE,
        )

        return TokenPair(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=UserInfo)
def read_me(current_user: User = Depends(get_current_user)):
    client = AuthGrpcClient()
    try:
        response = client.get_user_by_id(current_user.user_id)
        if not response:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}", response_model=UserInfo)
def read_user(
    user_id: str = Path(..., description="User UUID"),
    current_user: User = Depends(get_current_user),
):
    client = AuthGrpcClient()
    try:
        response = client.get_user_by_id(user_id)
        if not response:
            raise HTTPException(
                status_code=401,
                detail="Cannot read the user. Not exists or invalid UUID",
            )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_access_token(request: Request, settings: Settings = Depends(get_settings)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        email = payload.get("email")
        jti = payload.get("jti")

        if redis_client.get(f"bl:{jti}"):
            raise HTTPException(status_code=401, detail="Token revoked")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        new_access_token = create_access_token(
            data={"sub": user_id, "email": email},
            secret_key=settings.JWT_SECRET,
            algo=settings.JWT_ALGORITHM,
            expires_delta=settings.ACCESS_TOKEN_EXPIRE,
        )

        return {"access_token": new_access_token}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@router.patch("/me", response_model=UserInfo)
def update_user(
    data: UserUpdateRequest, current_user: User = Depends(get_current_user)
):
    client = AuthGrpcClient()
    try:
        response = client.update_user(
            name=data.name,
            surname=data.surname,
            email=current_user.email,
            password=data.password,
        )
        if not response:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/img", response_model=ImageResponse)
def get_user_img(current_user: User = Depends(get_current_user)):
    client = AuthGrpcClient()
    try:
        response = client.get_user_by_id(uuid=current_user.user_id)
        if not response:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        url = response.img_url
        return ImageResponse(url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/me/img", response_model=UserInfo)
def update_user_img(
    file: UploadFile = File(...), current_user: User = Depends(get_current_user)
):
    client = AuthGrpcClient()
    try:
        ext = os.path.splitext(file.filename)[1]
        file_name = f"{current_user.user_id}_{uuid4().hex}{ext}"
        url = upload_file(
            bucket_name="avatars",
            file_data=file.file,
            file_name=file_name,
            content_type=file.content_type,
        )
        response = client.update_user_img(email=current_user.email, img_url=url)
        if not response:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/me", response_model=MessageResponse)
def delete_user(current_user: User = Depends(get_current_user)):
    client = AuthGrpcClient()
    try:
        response = client.delete_user(email=current_user.email)
        if not response:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[UserOut])
def search_users(substr: str, current_user: User = Depends(get_current_user)):
    client = AuthGrpcClient()
    try:
        response = client.search_users(substr=substr)
        return [
            UserOut(user_id=u.user_id, name=u.name, surname=u.surname, email=u.email)
            for u in response.users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
