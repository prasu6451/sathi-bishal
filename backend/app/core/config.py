"""
Central Core Configuration for SATHI FastAPI Backend.
Uses pydantic-settings to safely load environment variables.
"""

from pathlib import Path
from typing import List, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings class."""

    PROJECT_NAME: str = "SATHI — AI-based Landslide Early-Warning System"
    API_V1_STR: str = "/api/v1"

    # Database URL (MySQL 8+ with PyMySQL)
    DATABASE_URL: str = Field(
        default="mysql+pymysql://root:password@localhost:3306/sathi",
        description="MySQL 8 Database URL"
    )

    # AI Model Configuration
    MODEL_DIR: str = Field(default="../ai/saved_models/current", description="Path to model artifacts")
    MODEL_VERSION: str = Field(default="xgb-v1", description="Authoritative AI Model Version")

    # Worker & Monitoring Settings
    RISK_UPDATE_INTERVAL_SECONDS: int = Field(default=60, description="Risk update loop interval")
    SIMULATION_MODE: bool = Field(default=False, description="Development simulation mode flag")
    ALPHAEARTH_PROVIDER: str = Field(default="real", description="AlphaEarth Satellite Provider ('real' or 'unavailable')")
    EARTHENGINE_PROJECT: str = Field(default="sathi-507115", description="Google Earth Engine Project ID")



    # External APIs
    WEATHER_API_URL: str = Field(default="https://api.open-meteo.com/v1/forecast")
    WEATHER_API_KEY: str = Field(default="")

    # CORS Origins
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    )
    LOG_LEVEL: str = Field(default="INFO")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def parsed_cors_origins(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS


settings = Settings()
