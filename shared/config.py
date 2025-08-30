"""
ShopEAT Shared Configuration
Common settings and constants used across the application
"""

import os
from typing import Dict, Any

# Environment configuration
ENV = os.getenv("ENV", "development")
DEBUG = ENV == "development"

# Server configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "3000"))

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "150"))

# WebSocket configuration
WS_PING_INTERVAL = 30  # seconds
WS_PING_TIMEOUT = 10   # seconds

# Voice processing configuration
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_FORMAT = "wav"

# Shopping categories
SHOPPING_CATEGORIES = [
    "dairy",
    "produce",
    "meat",
    "pantry",
    "frozen",
    "beverages",
    "snacks",
    "household",
    "personal_care",
    "general"
]

# Default shopping item template
DEFAULT_SHOPPING_ITEM = {
    "name": "",
    "quantity": 1,
    "category": "general",
    "notes": ""
}

# API endpoints
API_ENDPOINTS = {
    "health": "/health",
    "shopping_list": "/api/shopping-list",
    "websocket": "/ws/{client_id}"
}

# CORS origins for development
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
    }
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary"""
    return {
        "env": ENV,
        "debug": DEBUG,
        "backend": {
            "host": BACKEND_HOST,
            "port": BACKEND_PORT
        },
        "frontend": {
            "port": FRONTEND_PORT
        },
        "openai": {
            "model": OPENAI_MODEL,
            "max_tokens": OPENAI_MAX_TOKENS,
            "configured": bool(OPENAI_API_KEY)
        },
        "websocket": {
            "ping_interval": WS_PING_INTERVAL,
            "ping_timeout": WS_PING_TIMEOUT
        },
        "voice": {
            "sample_rate": AUDIO_SAMPLE_RATE,
            "channels": AUDIO_CHANNELS,
            "format": AUDIO_FORMAT
        }
    }
