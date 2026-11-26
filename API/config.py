"""
Configuration management for the FastAPI application using Pydantic Settings.
Loads environment variables from .env with fallback options.
"""
from typing import List, Optional, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Supabase connection settings
    SUPABASE_URL: str = Field(default="", description="Supabase project URL")
    SUPABASE_KEY: Optional[str] = Field(default=None, description="General Supabase API key")
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None, description="Supabase anon public key")
    SUPABASE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, description="Supabase publishable key")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None, description="Supabase service role key (admin)")
    SUPABASE_JWT_SECRET: Optional[str] = Field(default=None, description="Supabase JWT secret for verification")

    # API Server configuration
    API_TITLE: str = "Rafael Supabase API"
    API_DESCRIPTION: str = "REST API connecting Rafael with Supabase, enforcing Supabase Auth and RLS"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # CORS configuration (accepts string like "*" or list)
    CORS_ORIGINS: Union[str, List[str]] = Field(default="*")

    def get_cors_origins(self) -> List[str]:
        """
        Parses CORS_ORIGINS into a clean List[str].
        """
        if isinstance(self.CORS_ORIGINS, str):
            if self.CORS_ORIGINS.strip() == "*":
                return ["*"]
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS

    def get_supabase_key(self) -> str:
        """
        Returns the active Supabase public / anon key from environment variables.
        Supports SUPABASE_KEY, SUPABASE_PUBLISHABLE_KEY, and SUPABASE_ANON_KEY.
        """
        key = self.SUPABASE_KEY or self.SUPABASE_PUBLISHABLE_KEY or self.SUPABASE_ANON_KEY
        if not key:
            raise ValueError(
                "Supabase API key is missing. Set SUPABASE_PUBLISHABLE_KEY, SUPABASE_ANON_KEY, "
                "or SUPABASE_KEY in your .env file."
            )
        return key

    def get_supabase_url(self) -> str:
        """
        Returns the configured Supabase URL.
        """
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is missing. Please configure it in your .env file.")
        return self.SUPABASE_URL


settings = Settings()
