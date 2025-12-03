import time
import jwt


def create_access_token(
    data: dict,
    secret_key: str,
    algorithm: str,
    expires_in: int
) -> str:
    to_encode = data.copy()
    expire = int(time.time()) + expires_in
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def create_refresh_token(
    data: dict,
    secret_key: str,
    algorithm: str,
    expires_in: int
) -> str:
    to_encode = data.copy()
    expire = int(time.time()) + expires_in
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_jwt_token(
    token: str,
    secret_key: str,
    algorithm: str
) -> dict | None:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None
