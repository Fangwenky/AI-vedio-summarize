"""配置模块"""
from .settings import (
    LLM_CONFIG,
    LLM_PROVIDERS,
    OUTPUT_DIR,
    PROJECT_ROOT,
    TEMP_DIR,
    VIDEO_CONFIG,
    WHISPER_CONFIG,
    PPT_CONFIG,
)
from .api_manager import APIManager, api_manager

__all__ = [
    "PROJECT_ROOT",
    "OUTPUT_DIR",
    "TEMP_DIR",
    "VIDEO_CONFIG",
    "WHISPER_CONFIG",
    "PPT_CONFIG",
    "LLM_CONFIG",
    "LLM_PROVIDERS",
    "APIManager",
    "api_manager",
]
