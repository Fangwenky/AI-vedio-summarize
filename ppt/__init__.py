"""PPT检测模块"""
from .clarity_checker import ClarityChecker, check_clarity, filter_blurry_frames
from .ocr_extractor import OCRExtractor, extract_text, extract_texts_from_images
from .slide_detector import SlideDetector, detect_slides

__all__ = [
    "SlideDetector",
    "detect_slides",
    "ClarityChecker",
    "check_clarity",
    "filter_blurry_frames",
    "OCRExtractor",
    "extract_text",
    "extract_texts_from_images",
]
