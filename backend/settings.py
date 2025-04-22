from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr  

class EmailSettings(BaseSettings):  
    email_host: str  
    email_port: int  
    email_username: str  
    email_password: SecretStr  

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")  


class RedisSettings(BaseSettings):  
    redis_host: str  
    redis_port: int  
    redis_db: int  

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")  

    @property  
    def redis_url(self):  
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
class Settings(BaseSettings):   
    email_settings: EmailSettings = EmailSettings()  
    redis_settings: RedisSettings = RedisSettings()  

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")  


settings = Settings()
