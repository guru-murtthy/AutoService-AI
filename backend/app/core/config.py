import os
import logging
from typing import List
from pydantic_settings import BaseSettings

logger = logging.getLogger("config")

class Settings(BaseSettings):
    PROJECT_NAME: str = "AutoService AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    ENVIRONMENT: str = "development"  # development / production / test
    APP_ENV: str = "development"
    APP_MODE: str = "pilot"           # pilot / development / production / test
    DEMO_MODE: bool = False
    BUSINESS_VALIDATION_MODE: bool = True
    LOG_LEVEL: str = "INFO"

    # Domains & CORS
    CORS_ORIGINS: str = "*"
    PUBLIC_BASE_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # Security
    JWT_SECRET: str = "super-secret-jwt-key-autoservice-ai-change-in-production-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    DATABASE_URL: str = "sqlite:///./autoservice.db"

    # AI Provider
    AI_PROVIDER: str = "gemini"  # gemini / openai / mock
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    AI_TIMEOUT_SECONDS: float = 12.0
    AI_MAX_RETRIES: int = 3

    # Conway Automaton Integration
    AUTOMATON_ENABLED: bool = False
    AUTOMATON_URL: str = "http://localhost:9000"
    AUTOMATON_API_KEY: str = ""

    # Channel Integrations
    WHATSAPP_ENABLED: bool = False
    WHATSAPP_PROVIDER: str = "mock"
    WHATSAPP_API_KEY: str = ""
    PAYMENT_PROVIDER: str = "mock"
    PAYMENT_API_KEY: str = ""

    # Safety & Financial Feature Flags
    LIVE_TRADING_ENABLED: bool = False
    PAYMENTS_ENABLED: bool = False
    AUTONOMOUS_SPENDING_ENABLED: bool = False
    SELF_MODIFICATION_ENABLED: bool = False

    # Financial Safety Limits (₹ INR)
    DAILY_SPENDING_LIMIT: float = 500.0
    MONTHLY_SPENDING_LIMIT: float = 5000.0
    MINIMUM_RESERVE: float = 5000.0
    APPROVAL_THRESHOLD: float = 10000.0

    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def validate_production_secrets(self):
        if self.ENVIRONMENT.lower() == "production":
            if "change-in-production" in self.JWT_SECRET or len(self.JWT_SECRET) < 16:
                raise ValueError("SECURITY BLOCKER: JWT_SECRET must be configured with a strong key in production!")
            if self.CORS_ORIGINS == "*":
                logger.warning("SECURITY WARNING: Wildcard CORS_ORIGINS '*' set in production! Configure explicit domains.")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
settings.validate_production_secrets()
