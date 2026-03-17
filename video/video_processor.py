"""
视频基本信息获取模块
"""
import os
from pathlib import Path
from typing import Dict, Optional

import cv2


class VideoProcessor:
    """视频处理器 - 获取视频基本信息"""

    def __init__(self, video_path: str):
        self.video_path = video_path
        self.cap = None
        self._open()

    def _open(self):
        """打开视频文件"""
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.video_path}")

    def get_info(self) -> Dict:
        """获取视频基本信息"""
        return {
            "fps": self.get_fps(),
            "frame_count": self.get_frame_count(),
            "duration": self.get_duration(),
            "width": self.get_width(),
            "height": self.get_height(),
            "format": self.get_format(),
        }

    def get_fps(self) -> float:
        """获取帧率"""
        return self.cap.get(cv2.CAP_PROP_FPS)

    def get_frame_count(self) -> int:
        """获取总帧数"""
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_duration(self) -> float:
        """获取视频时长(秒)"""
        fps = self.get_fps()
        frame_count = self.get_frame_count()
        return frame_count / fps if fps > 0 else 0

    def get_width(self) -> int:
        """获取视频宽度"""
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    def get_height(self) -> int:
        """获取视频高度"""
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_format(self) -> str:
        """获取视频格式"""
        return Path(self.video_path).suffix[1:].lower()

    def get_frame(self, frame_number: int):
        """获取指定帧"""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def get_frame_at_time(self, time_seconds: float):
        """获取指定时间的帧"""
        fps = self.get_fps()
        frame_number = int(time_seconds * fps)
        return self.get_frame(frame_number)

    def release(self):
        """释放资源"""
        if self.cap:
            self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def get_video_info(video_path: str) -> Dict:
    """获取视频信息的便捷函数"""
    with VideoProcessor(video_path) as vp:
        return vp.get_info()
