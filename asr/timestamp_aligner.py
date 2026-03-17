"""
时间戳对齐模块 - 将PPT时间点与语音段落关联
"""
from typing import Dict, List, Tuple


class TimestampAligner:
    """时间戳对齐器 - 使用双指针对齐PPT和语音"""

    def __init__(self):
        pass

    def align(
        self,
        slide_times: List[float],
        speech_segments: List[Dict],
    ) -> List[Dict]:
        """
        对齐幻灯片和时间戳

        Args:
            slide_times: 幻灯片时间点列表(秒)
            speech_segments: 语音段落列表，每项包含 start, end, text

        Returns:
            对齐后的结果列表
        """
        if not slide_times or not speech_segments:
            return []

        aligned = []
        slide_idx = 0
        speech_idx = 0

        while slide_idx < len(slide_times) and speech_idx < len(speech_segments):
            slide_time = slide_times[slide_idx]
            segment = speech_segments[speech_idx]

            # 找到包含当前幻灯片时间的语音段落
            if segment["start"] <= slide_time <= segment["end"]:
                # 当前段落包含幻灯片时间
                aligned.append({
                    "slide_time": slide_time,
                    "slide_index": slide_idx,
                    "segment_start": segment["start"],
                    "segment_end": segment["end"],
                    "segment_text": segment["text"],
                    "speech_index": speech_idx,
                })
                slide_idx += 1
            elif slide_time > segment["end"]:
                # 幻灯片时间在当前段落之后，移动语音指针
                speech_idx += 1
            else:
                # 幻灯片时间在当前段落之前，可能需要特殊处理
                # 尝试移动幻灯片指针或寻找最近段落
                if slide_idx + 1 < len(slide_times):
                    # 检查下一个幻灯片时间
                    next_slide_time = slide_times[slide_idx + 1]
                    if next_slide_time <= segment["end"]:
                        # 当前段落包含下一个幻灯片时间
                        aligned.append({
                            "slide_time": slide_time,
                            "slide_index": slide_idx,
                            "segment_start": segment["start"],
                            "segment_end": segment["end"],
                            "segment_text": segment["text"],
                            "speech_index": speech_idx,
                        })
                        slide_idx += 1
                    else:
                        speech_idx += 1
                else:
                    break

        return aligned

    def get_closest_segment(
        self, time_point: float, speech_segments: List[Dict]
    ) -> Tuple[Dict, float]:
        """
        找到最接近时间点的语音段落

        Args:
            time_point: 目标时间点(秒)
            speech_segments: 语音段落列表

        Returns:
            (最近的语音段落, 时间差)
        """
        if not speech_segments:
            return None, float("inf")

        closest_segment = None
        min_diff = float("inf")

        for segment in speech_segments:
            # 计算段落中心点
            segment_center = (segment["start"] + segment["end"]) / 2
            diff = abs(segment_center - time_point)

            if diff < min_diff:
                min_diff = diff
                closest_segment = segment

        return closest_segment, min_diff

    def align_by_closest(
        self,
        slide_times: List[float],
        speech_segments: List[Dict],
    ) -> List[Dict]:
        """
        使用最近邻方式对齐

        Args:
            slide_times: 幻灯片时间点列表
            speech_segments: 语音段落列表

        Returns:
            对齐后的结果
        """
        aligned = []

        for i, slide_time in enumerate(slide_times):
            segment, diff = self.get_closest_segment(slide_time, speech_segments)

            if segment:
                aligned.append({
                    "slide_time": slide_time,
                    "slide_index": i,
                    "segment_start": segment["start"],
                    "segment_end": segment["end"],
                    "segment_text": segment["text"],
                    "time_diff": diff,
                })

        return aligned

    def generate_context_for_slide(
        self,
        slide_time: float,
        speech_segments: List[Dict],
        context_before: float = 5.0,
        context_after: float = 10.0,
    ) -> str:
        """
        为幻灯片生成上下文文字

        Args:
            slide_time: 幻灯片时间点
            speech_segments: 语音段落列表
            context_before: 幻灯片前的上下文时间(秒)
            context_after: 幻灯片后的上下文时间(秒)

        Returns:
            上下文文字
        """
        context_parts = []

        # 收集幻灯片前后的语音段落
        for segment in speech_segments:
            if segment["end"] < slide_time - context_before:
                continue
            if segment["start"] > slide_time + context_after:
                break

            context_parts.append(segment["text"])

        return " ".join(context_parts)


def align_timestamps(slide_times: List[float], speech_segments: List[Dict]) -> List[Dict]:
    """对齐时间戳的便捷函数"""
    aligner = TimestampAligner()
    return aligner.align(slide_times, speech_segments)
