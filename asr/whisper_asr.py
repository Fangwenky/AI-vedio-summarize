"""
Whisper语音转写模块 - 支持本地模型和API
"""
import os
from pathlib import Path
from typing import Dict, List, Optional

import whisper
from tqdm import tqdm


class WhisperASR:
    """Whisper语音识别器"""

    def __init__(self, model_size: str = "base", device: str = "cpu", language: str = "zh"):
        self.model_size = model_size
        self.device = device
        self.language = language
        self.model = None

    def load_model(self):
        """加载Whisper模型"""
        if self.model is None:
            print(f"加载 Whisper {self.model_size} 模型...")
            self.model = whisper.load_model(self.model_size, device=self.device)
            print("模型加载完成")

    def transcribe(
        self, audio_path: str, verbose: bool = True
    ) -> List[Dict]:
        """
        转写音频

        Args:
            audio_path: 音频文件路径
            verbose: 是否显示进度

        Returns:
            转写结果列表，每项包含 start, end, text
        """
        self.load_model()

        # 转写参数
        result = self.model.transcribe(
            audio_path,
            language=self.language,
            verbose=verbose,
            word_timestamps=True,
        )

        # 转换为标准格式
        segments = []
        for segment in result["segments"]:
            segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
            })

        return segments

    def transcribe_with_timestamps(
        self, audio_path: str
    ) -> Dict:
        """
        转写音频，返回完整结果

        Args:
            audio_path: 音频文件路径

        Returns:
            完整转写结果
        """
        self.load_model()

        result = self.model.transcribe(
            audio_path,
            language=self.language,
            verbose=False,
            word_timestamps=True,
        )

        return {
            "text": result["text"].strip(),
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"].strip(),
                }
                for seg in result["segments"]
            ],
            "language": result.get("language", self.language),
        }


class WhisperAPI:
    """Whisper API转写器(如果需要使用OpenAI API)"""

    def __init__(self, api_key: str):
        import openai
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)

    def transcribe(self, audio_path: str, language: str = "zh") -> Dict:
        """
        使用OpenAI Whisper API转写

        Args:
            audio_path: 音频文件路径
            language: 语言代码

        Returns:
            转写结果
        """
        with open(audio_path, "rb") as f:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        # 转换为标准格式
        segments = []
        for segment in response.segments:
            segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
            })

        return {
            "text": response.text.strip(),
            "segments": segments,
        }


def transcribe_audio(
    audio_path: str,
    model_size: str = "base",
    device: str = "cpu",
    language: str = "zh",
) -> List[Dict]:
    """转写音频的便捷函数(使用本地模型)"""
    asr = WhisperASR(model_size=model_size, device=device, language=language)
    return asr.transcribe(audio_path)
