"""
音频提取模块 - 使用ffmpeg从视频中提取音频
"""
import os
from pathlib import Path

# 设置ffmpeg路径
ffmpeg_bin = r"C:\Users\26299\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
if os.path.exists(ffmpeg_bin):
    os.environ['PATH'] = ffmpeg_bin + os.pathsep + os.environ.get('PATH', '')

import ffmpeg


class AudioExtractor:
    """音频提取器"""

    def __init__(self, video_path: str, output_dir: str = None):
        self.video_path = video_path
        self.output_dir = output_dir or str(Path(video_path).parent)
        self.output_path = None

    def extract(self, audio_format: str = "wav", sample_rate: int = 16000) -> str:
        """
        提取音频

        Args:
            audio_format: 输出音频格式 (wav, mp3, m4a)
            sample_rate: 采样率

        Returns:
            输出音频文件路径
        """
        video_name = Path(self.video_path).stem
        self.output_path = os.path.join(
            self.output_dir, f"{video_name}_audio.{audio_format}"
        )

        # 使用ffmpeg提取音频
        stream = ffmpeg.input(self.video_path)
        stream = ffmpeg.output(
            stream,
            self.output_path,
            acodec="pcm_s16le" if audio_format == "wav" else "copy",
            ar=sample_rate,
            ac=1,  # 单声道
        )

        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        return self.output_path

    def extract_with_ffmpeg(
        self, audio_format: str = "wav", sample_rate: int = 16000
    ) -> str:
        """
        使用ffmpeg-python提取音频(备用方法)

        Args:
            audio_format: 输出音频格式
            sample_rate: 采样率

        Returns:
            输出音频文件路径
        """
        video_name = Path(self.video_path).stem
        self.output_path = os.path.join(
            self.output_dir, f"{video_name}_audio.{audio_format}"
        )

        try:
            probe = ffmpeg.probe(self.video_path)
            # 检查是否已有音频流
            audio_streams = [
                s for s in probe["streams"] if s["codec_type"] == "audio"
            ]

            if not audio_streams:
                raise ValueError("视频文件中没有音频流")

            stream = ffmpeg.input(self.video_path)

            if audio_format == "wav":
                stream = ffmpeg.output(
                    stream,
                    self.output_path,
                    acodec="pcm_s16le",
                    ar=sample_rate,
                    ac=1,
                )
            else:
                stream = ffmpeg.output(
                    stream, self.output_path, acodec="copy", ar=sample_rate
                )

            ffmpeg.run(stream, overwrite_output=True, quiet=True)

        except ffmpeg.Error as e:
            raise RuntimeError(f"音频提取失败: {e.stderr.decode()}")

        return self.output_path


def extract_audio(video_path: str, output_dir: str = None) -> str:
    """提取音频的便捷函数"""
    extractor = AudioExtractor(video_path, output_dir)
    return extractor.extract()
