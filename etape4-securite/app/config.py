"""
Security Configuration for Digital Social Score API
"""
import os
from datetime import timedelta
from typing import List
from pydantic import BaseSettings

class SecuritySettings(BaseSettings):
    # JWT Configuration
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # API Keys
    master_api_key: str = "dss-master-key-change-in-production"
    admin_api_key: str = "dss-admin-key-change-in-production"
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 10
    redis_url: str = "redis://localhost:6379/0"
    
    # CORS & Security
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    force_https: bool = False
    
    # SSL/TLS
    ssl_cert_path: str = "./certs/cert.pem"
    ssl_key_path: str = "./certs/key.pem"
    
    # Logging
    log_level: str = "INFO"
    enable_access_logs: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

class AppSettings(BaseSettings):
    # Application
    api_title: str = "Digital Social Score API"
    api_description: str = "API sécurisée pour la détection de toxicité - Conforme RGPD"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Models
    bert_model_path: str = "../etape2-modele-ia/models/bert_model"
    simple_model_path: str = "../etape2-modele-ia/models/simple_model"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instances
security_settings = SecuritySettings()
app_settings = AppSettings()

# JWT Configuration
JWT_SECRET_KEY = security_settings.jwt_secret_key
JWT_ALGORITHM = security_settings.jwt_algorithm
JWT_EXPIRATION_DELTA = timedelta(hours=security_settings.jwt_expiration_hours)

# API Configuration  
API_TITLE = app_settings.api_title
API_DESCRIPTION = app_settings.api_description
API_VERSION = app_settings.api_version
DEBUG = app_settings.debug

# Security Configuration
ALLOWED_HOSTS = security_settings.allowed_hosts
CORS_ORIGINS = security_settings.cors_origins
FORCE_HTTPS = security_settings.force_https

# Rate Limiting
RATE_LIMIT_PER_MINUTE = security_settings.rate_limit_per_minute
RATE_LIMIT_BURST = security_settings.rate_limit_burst
REDIS_URL = security_settings.redis_url

# Logging
LOG_LEVEL = security_settings.log_level
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
