"""
PPT幻灯片检测模块 - 使用SSIM相似度计算进行去重
"""
import os
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm


class SlideDetector:
    """幻灯片检测器 - 通过相似度计算过滤重复帧"""

    def __init__(self, similarity_threshold: float = 0.9):
        self.similarity_threshold = similarity_threshold

    def load_image(self, image_path: str) -> np.ndarray:
        """加载图像并转换为灰度"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图像: {image_path}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """计算两张图像的SSIM相似度"""
        # 调整图像大小以加速计算
        h, w = min(img1.shape[0], img2.shape[0]), min(img1.shape[1], img2.shape[1])
        img1_resized = cv2.resize(img1, (w, h))
        img2_resized = cv2.resize(img2, (w, h))

        # 计算SSIM
        score, _ = ssim(img1_resized, img2_resized, full=True)
        return score

    def filter_similar_frames(
        self, frame_paths: List[str]
    ) -> Tuple[List[str], List[float]]:
        """
        过滤相似的帧

        Args:
            frame_paths: 帧文件路径列表

        Returns:
            (过滤后的帧路径列表, 对应相似度分数列表)
        """
        if not frame_paths:
            return [], []

        unique_frames = []
        similarities = []

        # 加载第一帧作为参考
        current_img = self.load_image(frame_paths[0])
        unique_frames.append(frame_paths[0])
        similarities.append(1.0)

        # 逐帧比较
        for path in tqdm(frame_paths[1:], desc="幻灯片检测"):
            img = self.load_image(path)
            similarity = self.calculate_similarity(current_img, img)

            # 如果相似度低于阈值，视为新的幻灯片
            if similarity < self.similarity_threshold:
                unique_frames.append(path)
                similarities.append(similarity)
                current_img = img

        return unique_frames, similarities

    def get_unique_slides(
        self, frame_paths: List[str], time_points: List[float] = None
    ) -> List[dict]:
        """
        获取唯一幻灯片及其时间点

        Args:
            frame_paths: 帧文件路径列表
            time_points: 对应的时间点列表

        Returns:
            幻灯片信息列表
        """
        unique_frames, similarities = self.filter_similar_frames(frame_paths)

        slides = []
        for i, (frame_path, similarity) in enumerate(zip(unique_frames, similarities)):
            slide_info = {
                "index": i,
                "path": frame_path,
                "similarity": similarity,
            }

            if time_points and i < len(time_points):
                slide_info["time"] = time_points[i]

            slides.append(slide_info)

        return slides


def detect_slides(frame_paths: List[str], threshold: float = 0.9) -> List[str]:
    """检测幻灯片的便捷函数"""
    detector = SlideDetector(similarity_threshold=threshold)
    unique_frames, _ = detector.filter_similar_frames(frame_paths)
    return unique_frames
