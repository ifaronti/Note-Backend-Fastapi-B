from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ALGORITHM:str
    JWT_ASHIRI:str
    TOKEN_EXPIRY:int
    DATABASE_URL:str
    PRISMA_PY_DEBUG_GENERATOR:int
    # CLIENT_ID:str
    # CLIENT_SECRET:str
    MAIL_PASSWORD:str
    MAIL_USERNAME:str  
    MAIL_FROM:str
    MAIL_PORT:int
    MAIL_SERVER:str
    MAIL_FROM_NAME:str    
    
    class Config:
        env_file = ".env"