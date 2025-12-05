from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenWeather API Configuration
    openweather_api_key: str = ""
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    
    # Cache Configuration
    cache_dir: str = "cache"
    cache_expiry_seconds: int = 300
    
    # API Configuration
    api_timeout: int = 10
    
    # Project root
    project_root: Path = Path(__file__).parent.parent.parent
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"
    
    @property
    def cache_path(self) -> Path:
        """Get the full cache directory path."""
        return self.project_root / self.cache_dir


settings = Settings()
