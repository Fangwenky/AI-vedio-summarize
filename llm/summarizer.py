"""
课程总结生成模块
"""
from typing import Dict, List, Optional

from .llm_client import LLMClient


class CourseSummarizer:
    """课程总结生成器"""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()

    def generate_summary(
        self,
        transcript: str,
        slides: List[Dict],
        title: str = "课程总结",
    ) -> str:
        """
        生成课程总结

        Args:
            transcript: 完整转写文本
            slides: 幻灯片信息列表，每项包含 text, time 等
            title: 课程标题

        Returns:
            总结内容
        """
        # 构建提示词
        prompt = self._build_summary_prompt(transcript, slides, title)

        messages = [
            {"role": "system", "content": "你是一个专业的课程总结助手，擅长从课程视频中提取关键信息，生成结构化的学习笔记。"},
            {"role": "user", "content": prompt},
        ]

        return self.llm_client.chat(messages)

    def _build_summary_prompt(self, transcript: str, slides: List[Dict], title: str) -> str:
        """构建总结提示词"""
        # 提取幻灯片文字
        slide_texts = []
        for i, slide in enumerate(slides):
            if slide.get("text"):
                slide_texts.append(f"幻灯片 {i+1}: {slide['text']}")

        slides_content = "\n".join(slide_texts) if slide_texts else "无"

        prompt = f"""请根据以下课程视频的转写文本和幻灯片内容，生成一份详细的课程总结。

课程标题: {title}

=== 幻灯片内容 ===
{slides_content}

=== 视频转写文本 ===
{transcript}

请生成以下内容:
1. 课程概述 (简短的课程介绍)
2. 主要知识点 (列出3-5个核心知识点)
3. 详细总结 (结合幻灯片和语音内容)
4. 关键要点 (列出5-8个关键要点)

注意:
- 使用中文输出
- 结合幻灯片文字和语音内容进行总结
- 保持内容的准确性和完整性
"""
        return prompt

    def generate_notes(
        self,
        transcript: str,
        slides: List[Dict],
    ) -> str:
        """
        生成课程笔记

        Args:
            transcript: 完整转写文本
            slides: 幻灯片信息列表

        Returns:
            课程笔记
        """
        # 构建笔记提示词
        prompt = self._build_notes_prompt(transcript, slides)

        messages = [
            {"role": "system", "content": "你是一个专业的学习笔记助手，擅长整理和归纳学习内容。"},
            {"role": "user", "content": prompt},
        ]

        return self.llm_client.chat(messages)

    def _build_notes_prompt(self, transcript: str, slides: List[Dict]) -> str:
        """构建笔记提示词"""
        # 提取幻灯片文字和时间点
        slide_parts = []
        for slide in slides:
            time_str = ""
            if slide.get("time") is not None:
                minutes = int(slide["time"] // 60)
                seconds = int(slide["time"] % 60)
                time_str = f"[{minutes:02d}:{seconds:02d}] "

            text = slide.get("text", "")
            if text:
                slide_parts.append(f"{time_str}{text}")

        slides_content = "\n".join(slide_parts) if slide_parts else "无"

        prompt = f"""请根据以下课程内容，生成结构化的学习笔记。

=== 幻灯片内容(带时间戳) ===
{slides_content}

=== 视频转写文本 ===
{transcript}

请生成详细的学习笔记，包括:
- 每张幻灯片对应的讲解内容
- 关键概念和定义
- 示例和案例(如果有)
- 要注意的要点

使用Markdown格式输出。
"""
        return prompt

    def generate_outline(
        self,
        transcript: str,
    ) -> str:
        """
        生成课程大纲

        Args:
            transcript: 完整转写文本

        Returns:
            课程大纲
        """
        prompt = f"""请根据以下视频转写文本，提取并生成课程大纲。

=== 转写文本 ===
{transcript}

请生成:
1. 课程标题(如果可以从内容中推断)
2. 章节大纲(按时间顺序列出主要章节)
3. 每个章节的核心要点

使用Markdown格式输出。
"""

        messages = [
            {"role": "system", "content": "你是一个专业的课程大纲生成助手。"},
            {"role": "user", "content": prompt},
        ]

        return self.llm_client.chat(messages)


def summarize_course(
    transcript: str,
    slides: List[Dict],
    provider: str = None,
    model: str = None,
) -> str:
    """生成课程总结的便捷函数"""
    client = LLMClient(provider=provider, model=model)
    summarizer = CourseSummarizer(llm_client=client)
    return summarizer.generate_summary(transcript, slides)
