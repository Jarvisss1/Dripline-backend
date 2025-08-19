from pydantic_settings import BaseSettings # <-- CORRECTED IMPORT

class Settings(BaseSettings):
    MONGO_DETAILS: str
    CLERK_ISSUER_URL: str
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
