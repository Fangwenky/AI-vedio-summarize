"""
视频抽帧模块
"""
import os
from pathlib import Path
from typing import List, Optional

import cv2
from tqdm import tqdm

from .video_processor import VideoProcessor


class FrameExtractor:
    """视频抽帧器"""

    def __init__(self, video_path: str, output_dir: str = None):
        self.video_path = video_path
        self.output_dir = output_dir or str(Path(video_path).parent)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def extract_frames(
        self,
        interval: float = 1.0,
        max_frames: Optional[int] = None,
        output_prefix: str = "frame",
    ) -> List[str]:
        """
        按固定间隔抽帧

        Args:
            interval: 抽帧间隔(秒)
            max_frames: 最大抽帧数量
            output_prefix: 输出文件前缀

        Returns:
            抽帧文件路径列表
        """
        frames = []

        with VideoProcessor(self.video_path) as vp:
            fps = vp.get_fps()
            duration = vp.get_duration()
            frame_interval = int(interval * fps)

            total_frames = int(duration / interval)
            if max_frames:
                total_frames = min(total_frames, max_frames)

            video_name = Path(self.video_path).stem

            for i in tqdm(range(total_frames), desc="抽帧中"):
                frame_time = i * interval
                frame = vp.get_frame_at_time(frame_time)

                if frame is not None:
                    output_path = os.path.join(
                        self.output_dir,
                        f"{video_name}_{output_prefix}_{i:05d}.jpg",
                    )
                    cv2.imwrite(output_path, frame)
                    frames.append(output_path)

        return frames

    def extract_keyframes(self, max_frames: int = 100) -> List[str]:
        """
        提取关键帧(均匀分布)

        Args:
            max_frames: 最大关键帧数量

        Returns:
            关键帧文件路径列表
        """
        frames = []

        with VideoProcessor(self.video_path) as vp:
            total_frame_count = vp.get_frame_count()
            frame_interval = max(1, total_frame_count // max_frames)

            video_name = Path(self.video_path).stem

            for i in tqdm(range(0, total_frame_count, frame_interval), desc="提取关键帧"):
                frame = vp.get_frame(i)
                if frame is not None:
                    output_path = os.path.join(
                        self.output_dir, f"{video_name}_keyframe_{i:05d}.jpg"
                    )
                    cv2.imwrite(output_path, frame)
                    frames.append(output_path)

        return frames

    def extract_frame_at_time(self, time_seconds: float, output_path: str = None) -> str:
        """
        提取指定时间的帧

        Args:
            time_seconds: 时间点(秒)
            output_path: 输出路径

        Returns:
            输出文件路径
        """
        with VideoProcessor(self.video_path) as vp:
            frame = vp.get_frame_at_time(time_seconds)

            if output_path is None:
                video_name = Path(self.video_path).stem
                output_path = os.path.join(
                    self.output_dir, f"{video_name}_time_{int(time_seconds)}s.jpg"
                )

            cv2.imwrite(output_path, frame)
            return output_path


def extract_frames(video_path: str, output_dir: str = None, interval: float = 1.0) -> List[str]:
    """抽帧的便捷函数"""
    extractor = FrameExtractor(video_path, output_dir)
    return extractor.extract_frames(interval=interval)
