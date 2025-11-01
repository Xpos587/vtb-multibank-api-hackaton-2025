from typing import Optional, List
from functools import lru_cache
import zoneinfo
from datetime import datetime

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings as _BaseSettings
from pydantic_settings import SettingsConfigDict


class BaseSettings(_BaseSettings):
    """Base settings class with common configuration"""

    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )


class AppConfig(BaseSettings):
    """Main application settings"""

    name: str = "backend"
    version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production
    host: str = "0.0.0.0"
    port: int = 8000
    timezone: str = "UTC"

    class Config:
        env_prefix = "APP_"


class DatabaseConfig(BaseSettings):
    """Database settings"""

    url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    url_async: Optional[str] = Field(default=None, alias="DATABASE_URL_ASYNC")

    host: str = "localhost"
    port: int = 5432
    db: str = "db"
    user: str = "postgres"
    password: SecretStr = SecretStr("password")
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600

    def build_dsn(self) -> str:
        """Generate connection string for PostgreSQL"""
        # If direct URL is provided, use it
        if self.url:
            return self.url

        # Otherwise build from individual parameters
        password = self.password.get_secret_value()
        return f"postgresql://{self.user}:{password}@{self.host}:{self.port}/{self.db}"

    def build_async_dsn(self) -> str:
        """Generate async connection string for PostgreSQL"""
        # If direct async URL is provided, use it
        if self.url_async:
            return self.url_async

        # If regular URL is provided, convert to async
        if self.url:
            return self.url.replace("postgresql://", "postgresql+asyncpg://")

        # Otherwise build from individual parameters
        password = self.password.get_secret_value()
        return f"postgresql+asyncpg://{self.user}:{password}@{self.host}:{self.port}/{self.db}"

    class Config:
        env_prefix = "DATABASE_"


class SecurityConfig(BaseSettings):
    """Security and JWT settings"""

    jwt_private_key: SecretStr = SecretStr(
        "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg..."
    )
    jwt_public_key: SecretStr = SecretStr("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...")
    jwt_algorithm: str = "ES256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    max_failed_attempts: int = 10
    ip_block_duration: int = 300  # 5 minutes

    class Config:
        env_prefix = "SECURITY_"


class CORSConfig(BaseSettings):
    """CORS settings"""

    origins: List[str] = ["http://localhost:3000", "http://localhost:4321"]
    allow_credentials: bool = True
    max_age: int = 3600

    class Config:
        env_prefix = "CORS_"


class LoggingConfig(BaseSettings):
    """Logging settings"""

    level: str = "INFO"
    enable_request_logging: bool = True
    enable_sql_logging: bool = False

    # Hardcoded format - not configurable via environment
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_prefix = "LOG_"


class Settings(BaseSettings):
    """Main application settings with grouped configuration"""

    # Grouped settings
    app: AppConfig = Field(default_factory=AppConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @property
    def jwt_private_key(self) -> str:
        return self.security.jwt_private_key.get_secret_value()

    @property
    def jwt_public_key(self) -> str:
        return self.security.jwt_public_key.get_secret_value()

    @property
    def is_production(self) -> bool:
        """Check if environment is production"""
        return self.app.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if environment is development"""
        return self.app.environment.lower() == "development"

    def get_cors_origins(self) -> List[str]:
        """Get list of allowed CORS origins"""
        if self.is_development:
            return self.cors.origins + ["http://localhost:*"]
        return self.cors.origins

    @property
    def timezone_info(self) -> zoneinfo.ZoneInfo:
        """Get timezone object"""
        try:
            return zoneinfo.ZoneInfo(self.app.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            # Fallback to UTC if timezone is invalid
            return zoneinfo.ZoneInfo("UTC")

    def now(self) -> datetime:
        """Get current time in configured timezone"""
        return datetime.now(self.timezone_info)

    def utc_to_local(self, utc_dt: datetime) -> datetime:
        """Convert UTC time to local timezone"""
        if utc_dt.tzinfo is None:
            utc_dt = utc_dt.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
        return utc_dt.astimezone(self.timezone_info)

    def local_to_utc(self, local_dt: datetime) -> datetime:
        """Convert local time to UTC"""
        if local_dt.tzinfo is None:
            local_dt = local_dt.replace(tzinfo=self.timezone_info)
        return local_dt.astimezone(zoneinfo.ZoneInfo("UTC"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore additional fields

        # Support for nested environment variables
        env_nested_delimiter = "__"


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (with caching)"""
    return Settings()


settings = get_settings()
