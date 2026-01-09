from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "LLM Guard Manager"
    API_V1_STR: str = "/api/v1"
    # 使用 MySQL 作为默认数据库 (aiomysql 驱动)
    DATABASE_URL: str =  "mysql+aiomysql://root:123456abc@127.0.0.1:3306/llm_safe_db?charset=utf8mb4"
    class Config:
        case_sensitive = True

settings = Settings()
