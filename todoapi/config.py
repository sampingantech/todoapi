from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Todo API"
    todo_database_url: str
    items_per_user: int = 50

    class Config:
        env_file = ".env"


settings = Settings()
