from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    MY_API_KEY: str
    GEMINI_API_KEY: str
    DB_URL: str 
    SYSTEM_INSTRUCTION: str = "Please describe how the ai should respond to the user."

    class Config:
        env_file = ".env"


settings = Settings()
