from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "Ghibli API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="CHANGE_THIS_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENVIRONMENT: str = Field(default="development")
    PAGINATION_DEFAULT_LIMIT: int = Field(default=10)
    CREATE_INITIAL_DATA: bool = Field(default=False)

    # Database Configuration
    POSTGRES_USER: str = Field(default="user")
    POSTGRES_PASSWORD: str = Field(default="password")
    POSTGRES_DB: str = Field(default="ghibli_api")
    POSTGRES_HOST: str = Field(default="ghibli_db")
    POSTGRES_PORT: str = Field(default="5432")

    @property
    def DATABASE_URL(self) -> str:
        """Construye la URL de la base de datos usando las variables individuales"""
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(
        default="[%(levelname)s][%(filename)s:%(lineno)d][%(funcName)s]%(message)s"
    )
    LOG_DATE_FORMAT: str = Field(default="%Y-%m-%d %H:%M:%S")
    LOG_FILE: str = Field(default="app.log")
    LOG_USE_COLORS: bool = Field(default=True)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
