"""
Configuration management with environment variables
Uses pydantic-settings for type-safe configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Parametric Yantra Generator"
    VERSION: str = "0.6.0"
    
    # Security
    JWT_SECRET: str = "change-me-in-production-use-strong-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000"
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://yantra:yantra@localhost:5432/yantra"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL_SECONDS: int = 3600
    
    # Object Storage (Cloudflare R2 or MinIO)
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET_NAME: str = "yantra-exports"
    R2_ENDPOINT: str = ""  # Leave empty for Cloudflare R2, set for MinIO
    R2_PUBLIC_URL: str = ""  # CDN URL if configured
    
    # File Export Settings
    EXPORT_MAX_SIZE_MB: int = 50
    EXPORT_EXPIRY_HOURS: int = 24
    EXPORT_FORMATS: List[str] = ["dxf", "stl", "gltf", "step", "pdf"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # Astronomy/Ephemeris
    EPHEMERIS_DATA_PATH: str = "./data/ephemeris"
    WMM_DATA_PATH: str = "./data/wmm"
    ENABLE_EPHEMERIS_CACHE: bool = True
    
    # Generation Limits
    MAX_YANTRA_SCALE: float = 1000.0  # meters
    MIN_YANTRA_SCALE: float = 0.1  # meters
    MAX_CONCURRENT_GENERATIONS: int = 5
    GENERATION_TIMEOUT_SECONDS: int = 300
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Feature Flags
    ENABLE_AR_ENDPOINTS: bool = True
    ENABLE_COLLABORATIVE_MODE: bool = False
    ENABLE_CITIZEN_SCIENCE: bool = False
    ENABLE_AI_SUGGESTIONS: bool = True
    
    # Sentry (Error Tracking)
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # MapTiler (Optional, for better maps)
    MAPTILER_API_KEY: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting"""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS

# Initialize settings singleton
settings = Settings()

# Validation on startup
if settings.is_production():
    if settings.JWT_SECRET == "change-me-in-production-use-strong-secret":
        raise ValueError("JWT_SECRET must be changed in production!")
    if settings.DEBUG:
        raise ValueError("DEBUG must be False in production!")
    if not settings.R2_ACCESS_KEY or not settings.R2_SECRET_KEY:
        print("⚠️  Warning: R2 storage not configured. File exports will fail.")