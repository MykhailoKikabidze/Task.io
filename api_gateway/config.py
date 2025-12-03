from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS: str = Field("kafka:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")

    ACCESS_TOKEN_EXPIRE: int = Field(900, env="ACCESS_TOKEN_EXPIRE")
    REFRESH_TOKEN_EXPIRE: int = Field(86400, env="REFRESH_TOKEN_EXPIRE")

    MINIO_ENDPOINT: str = Field(env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(env="MINIO_SECRET_KEY")
    MINIO_PUBLIC_HOST: str = Field(env="MINIO_PUBLIC_HOST")

    REDIS_URL: str = Field(env="REDIS_URL")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
