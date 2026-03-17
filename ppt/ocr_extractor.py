"""
OCR文字提取模块 - 从幻灯片图像中提取文字
"""
import os
from pathlib import Path
from typing import Dict, List, Optional

import pytesseract
from PIL import Image
from tqdm import tqdm


class OCRExtractor:
    """OCR文字提取器"""

    def __init__(self, lang: str = "chi_sim+eng"):
        self.lang = lang
        # 配置tesseract路径(Windows需要)
        # 如果需要自定义路径，使用: pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def extract_text(self, image_path: str) -> str:
        """
        从图像中提取文字

        Args:
            image_path: 图像文件路径

        Returns:
            提取的文字
        """
        img = Image.open(image_path)

        # 配置OCR选项
        custom_config = r"--oem 3 --psm 6"

        text = pytesseract.image_to_string(
            img, lang=self.lang, config=custom_config
        )

        # 清理文本
        text = self.clean_text(text)
        return text

    def clean_text(self, text: str) -> str:
        """清理OCR提取的文本"""
        # 移除多余空白
        lines = text.split("\n")
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(cleaned_lines)

    def extract_from_multiple(
        self, image_paths: List[str], time_points: List[float] = None
    ) -> List[Dict]:
        """
        从多张图像提取文字

        Args:
            image_paths: 图像文件路径列表
            time_points: 对应的时间点列表

        Returns:
            提取结果列表
        """
        results = []

        for i, path in enumerate(tqdm(image_paths, desc="OCR提取")):
            try:
                text = self.extract_text(path)
                result = {
                    "index": i,
                    "path": path,
                    "text": text,
                    "char_count": len(text),
                }

                if time_points and i < len(time_points):
                    result["time"] = time_points[i]

                results.append(result)
            except Exception as e:
                print(f"警告: OCR处理 {path} 时出错: {e}")
                results.append({
                    "index": i,
                    "path": path,
                    "text": "",
                    "error": str(e),
                })

        return results

    def extract_with_boxes(self, image_path: str) -> Dict:
        """
        提取文字及位置信息

        Args:
            image_path: 图像文件路径

        Returns:
            包含文字和位置信息的字典
        """
        img = Image.open(image_path)

        # 获取文字数据和包围盒
        data = pytesseract.image_to_data(
            img, lang=self.lang, output_type=pytesseract.Output.DICT
        )

        words = []
        n = len(data["text"])
        for i in range(n):
            text = data["text"][i].strip()
            if text:
                words.append({
                    "text": text,
                    "x": data["left"][i],
                    "y": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                    "confidence": data["conf"][i],
                })

        return {
            "path": image_path,
            "words": words,
            "full_text": " ".join([w["text"] for w in words]),
        }


def extract_text(image_path: str, lang: str = "chi_sim+eng") -> str:
    """提取文字的便捷函数"""
    extractor = OCRExtractor(lang=lang)
    return extractor.extract_text(image_path)


def extract_texts_from_images(
    image_paths: List[str], lang: str = "chi_sim+eng"
) -> List[Dict]:
    """从多张图像提取文字的便捷函数"""
    extractor = OCRExtractor(lang=lang)
    return extractor.extract_from_multiple(image_paths)
