from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    POSTGRES_USER: str = "team_manager"
    POSTGRES_PASSWORD: str = "team_manager_pass"
    POSTGRES_DB: str = "team_manager_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: str = "postgresql+psycopg://team_manager:team_manager_pass@localhost:5432/team_manager_db"

    # Application
    APP_NAME: str = "Team Manager API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()