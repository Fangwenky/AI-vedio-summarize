"""
全局配置管理模块
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 临时文件目录
TEMP_DIR = PROJECT_ROOT / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# 视频处理配置
VIDEO_CONFIG = {
    "max_duration": 3600,  # 最大视频时长(秒)
    "supported_formats": ["mp4", "avi", "mov", "mkv"],
    "frame_sample_rate": 1,  # 每秒抽帧数
}

# PPT检测配置
PPT_CONFIG = {
    "similarity_threshold": 0.9,  # 相似度阈值
    "clarity_threshold": 100,  # 清晰度阈值(Laplacian方差)
    "min_slide_interval": 3,  # 最小幻灯片间隔(秒)
}

# Whisper配置
WHISPER_CONFIG = {
    "model_size": "base",  # 模型大小: tiny, base, small, medium, large
    "language": "zh",  # 语言: zh, en, auto
    "device": "cuda",  # 设备: cuda, cpu
}

# LLM配置
LLM_CONFIG = {
    "default_provider": "openai",  # 默认提供商
    "temperature": 0.7,
    "max_tokens": 4000,
}

# 支持的LLM提供商
LLM_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"],
    },
    "qwen": {
        "name": "阿里Qwen",
        "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
    },
    "minimax": {
        "name": "MiniMax",
        "models": [
            "MiniMax-M2.5",
            "MiniMax-M2.5-highspeed",
            "MiniMax-M2.1",
            "MiniMax-M2",
        ],
    },
}
