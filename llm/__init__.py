"""AI总结模块"""
from .llm_client import LLMClient, create_client
from .summarizer import CourseSummarizer, summarize_course

__all__ = [
    "LLMClient",
    "create_client",
    "CourseSummarizer",
    "summarize_course",
]
