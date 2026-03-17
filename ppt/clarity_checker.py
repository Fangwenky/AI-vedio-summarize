"""
清晰度检测模块 - 使用Laplacian方差检测图像模糊
"""
import os
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from tqdm import tqdm


class ClarityChecker:
    """清晰度检测器 - 过滤模糊的幻灯片图像"""

    def __init__(self, clarity_threshold: int = 100):
        self.clarity_threshold = clarity_threshold

    def calculate_laplacian_variance(self, image_path: str) -> float:
        """
        使用Laplacian方差计算图像清晰度

        方差越大表示图像越清晰
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"无法读取图像: {image_path}")

        # 计算Laplacian
        laplacian = cv2.Laplacian(img, cv2.CV_64F)
        variance = laplacian.var()
        return variance

    def is_clear(self, image_path: str) -> bool:
        """判断图像是否清晰"""
        variance = self.calculate_laplacian_variance(image_path)
        return variance >= self.clarity_threshold

    def filter_blurry_frames(
        self, frame_paths: List[str]
    ) -> Tuple[List[str], List[float]]:
        """
        过滤模糊的帧

        Args:
            frame_paths: 帧文件路径列表

        Returns:
            (清晰的帧路径列表, 对应清晰度分数列表)
        """
        clear_frames = []
        clarity_scores = []

        for path in tqdm(frame_paths, desc="清晰度检测"):
            try:
                variance = self.calculate_laplacian_variance(path)
                if variance >= self.clarity_threshold:
                    clear_frames.append(path)
                    clarity_scores.append(variance)
            except Exception as e:
                print(f"警告: 处理图像 {path} 时出错: {e}")
                continue

        return clear_frames, clarity_scores

    def get_clear_slides(
        self, frame_paths: List[str], time_points: List[float] = None
    ) -> List[dict]:
        """
        获取清晰幻灯片及其信息

        Args:
            frame_paths: 帧文件路径列表
            time_points: 对应的时间点列表

        Returns:
            清晰幻灯片信息列表
        """
        clear_frames, clarity_scores = self.filter_blurry_frames(frame_paths)

        slides = []
        # 建立原始索引到清晰帧的映射
        original_indices = []
        for path in clear_frames:
            if path in frame_paths:
                original_indices.append(frame_paths.index(path))

        for i, (frame_path, clarity) in enumerate(zip(clear_frames, clarity_scores)):
            slide_info = {
                "index": i,
                "path": frame_path,
                "clarity": clarity,
                "is_clear": True,
            }

            if time_points and original_indices[i] < len(time_points):
                slide_info["time"] = time_points[original_indices[i]]

            slides.append(slide_info)

        return slides


def check_clarity(image_path: str, threshold: int = 100) -> Tuple[bool, float]:
    """检查图像清晰度的便捷函数"""
    checker = ClarityChecker(clarity_threshold=threshold)
    variance = checker.calculate_laplacian_variance(image_path)
    return variance >= threshold, variance


def filter_blurry_frames(frame_paths: List[str], threshold: int = 100) -> List[str]:
    """过滤模糊帧的便捷函数"""
    checker = ClarityChecker(clarity_threshold=threshold)
    clear_frames, _ = checker.filter_blurry_frames(frame_paths)
    return clear_frames
