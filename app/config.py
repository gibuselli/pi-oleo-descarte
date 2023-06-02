from pydantic import BaseSettings


class Settings(BaseSettings):
    SIGN_IN_KEY: str
    PROJECT_NAME: str = "Oleo-Descarte"

    class Config:
        env_file = ".env"


settings = Settings()