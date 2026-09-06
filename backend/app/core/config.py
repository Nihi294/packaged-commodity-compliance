from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(validation_alias="DATABASE_URL")
    jwt_secret: str = Field(validation_alias="JWT_SECRET", min_length=32)
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    tesseract_cmd: str | None = Field(default=None, validation_alias="TESSERACT_CMD")
    upload_dir: str = Field(default="uploads", validation_alias="UPLOAD_DIR")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

if not settings.database_url.startswith("postgresql"):
    raise ValueError("DATABASE_URL must be a PostgreSQL connection URL")
