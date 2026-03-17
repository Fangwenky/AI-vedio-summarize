"""
Streamlit主界面 - AI课程录播总结工具
"""
import os
import time
from pathlib import Path

import cv2

# 解决OpenMP冲突问题
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# 添加ffmpeg到PATH (Windows winget安装位置)
ffmpeg_bin_path = r"C:\Users\26299\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
if os.path.exists(ffmpeg_bin_path):
    os.environ['PATH'] = ffmpeg_bin_path + os.pathsep + os.environ.get('PATH', '')
    os.environ['FFMPEG_BINARY'] = os.path.join(ffmpeg_bin_path, 'ffmpeg.exe')
    os.environ['FFPROBE_BINARY'] = os.path.join(ffmpeg_bin_path, 'ffprobe.exe')

import streamlit as st

# 添加项目根目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import api_manager, LLM_PROVIDERS
from asr import WhisperASR, transcribe_audio
from llm import CourseSummarizer
from ppt import SlideDetector, ClarityChecker, OCRExtractor
from video import extract_audio, extract_frames


# 页面配置
st.set_page_config(
    page_title="AI课程总结工具",
    page_icon="📚",
    layout="wide",
)


def init_session_state():
    """初始化会话状态"""
    if "video_info" not in st.session_state:
        st.session_state.video_info = None
    if "video_path" not in st.session_state:
        st.session_state.video_path = None
    if "audio_path" not in st.session_state:
        st.session_state.audio_path = None
    if "transcript" not in st.session_state:
        st.session_state.transcript = None
    if "transcript_text" not in st.session_state:
        st.session_state.transcript_text = None
    if "slides" not in st.session_state:
        st.session_state.slides = None
    if "summary" not in st.session_state:
        st.session_state.summary = None
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "processed" not in st.session_state:
        st.session_state.processed = False


def sidebar_config():
    """侧边栏配置"""
    st.sidebar.title("⚙️ 配置")

    # API配置
    st.sidebar.header("API 配置")

    # 选择提供商
    provider = st.sidebar.selectbox(
        "选择LLM服务商",
        options=list(LLM_PROVIDERS.keys()),
        format_func=lambda x: LLM_PROVIDERS[x]["name"],
        index=list(LLM_PROVIDERS.keys()).index(api_manager.get_provider()),
    )

    if provider != api_manager.get_provider():
        api_manager.set_provider(provider)

    # 选择模型
    models = LLM_PROVIDERS[provider]["models"]
    model = st.sidebar.selectbox(
        "选择模型",
        options=models,
        index=models.index(api_manager.get_model()) if api_manager.get_model() in models else 0,
    )

    if model != api_manager.get_model():
        api_manager.set_model(model)

    # API密钥输入
    if provider != "minimax":
        api_key = st.sidebar.text_input(
            "API密钥",
            type="password",
            value=api_manager.get_all_keys().get(provider, ""),
        )
        if api_key:
            api_manager.set_api_key(provider, api_key)
            st.sidebar.success("✓ API密钥已保存")
    else:
        # MiniMax使用Anthropic兼容API
        st.sidebar.subheader("MiniMax 配置")
        api_key = st.sidebar.text_input(
            "API密钥 (sk-cp-xxx)",
            type="password",
            key="minimax_api_key_input",
            help="从MiniMax平台获取接口密钥"
        )
        if api_key:
            st.sidebar.success("✓ MiniMax配置已保存")

    # Whisper配置
    st.sidebar.header("语音识别配置")
    whisper_model = st.sidebar.selectbox(
        "Whisper模型",
        ["tiny", "base", "small", "medium", "large"],
        index=1,  # default base
    )

    # PPT检测配置
    st.sidebar.header("PPT检测配置")
    similarity_threshold = st.sidebar.slider(
        "相似度阈值",
        min_value=0.7,
        max_value=0.99,
        value=0.9,
        step=0.01,
    )

    clarity_threshold = st.sidebar.slider(
        "清晰度阈值",
        min_value=50,
        max_value=200,
        value=100,
        step=10,
    )

    # 结果展示配置
    st.sidebar.header("结果展示")

    # 初始化显示选项
    if "show_transcript" not in st.session_state:
        st.session_state.show_transcript = False
    if "show_slides" not in st.session_state:
        st.session_state.show_slides = False

    # 转写结果显示选项
    st.sidebar.subheader("📝 转写文本")
    st.session_state.show_transcript = st.sidebar.checkbox(
        "显示转写文本",
        value=st.session_state.show_transcript,
        key="cb_transcript"
    )

    # PPT结果显示选项
    st.sidebar.subheader("📊 幻灯片")
    st.session_state.show_slides = st.sidebar.checkbox(
        "显示幻灯片",
        value=st.session_state.show_slides,
        key="cb_slides"
    )

    return {
        "whisper_model": whisper_model,
        "similarity_threshold": similarity_threshold,
        "clarity_threshold": clarity_threshold,
    }


def main_page(config):
    """主页面"""
    st.title("📚 AI课程录播总结工具")

    # 选择输入方式
    input_method = st.radio(
        "选择视频输入方式",
        ["上传视频文件", "输入本地文件路径"],
        horizontal=True,
    )

    video_path = None
    current_video_name = None

    if input_method == "上传视频文件":
        uploaded_file = st.file_uploader(
            "上传视频文件",
            type=["mp4", "avi", "mov", "mkv"],
            help="支持MP4、AVI、MOV、MKV格式（可处理大文件）",
        )

        if uploaded_file:
            # 保存上传的文件
            current_video_name = uploaded_file.name
            video_path = f"temp/{uploaded_file.name}"
            os.makedirs("temp", exist_ok=True)
            with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✓ 已上传: {uploaded_file.name}")
    else:
        # 输入本地文件路径
        local_path = st.text_input(
            "输入视频文件完整路径",
            placeholder="例如: D:\\Videos\\course.mp4",
            help="输入本地视频文件的完整路径",
        )
        if local_path and os.path.exists(local_path):
            video_path = local_path
            current_video_name = os.path.basename(local_path)
            st.success(f"✓ 已加载: {local_path}")
        elif local_path:
            st.error(f"文件不存在: {local_path}")

    # 检测视频是否变化，如果变化则清除之前的结果
    if video_path:
        # 检查是否是新的视频
        if st.session_state.get("current_video_name") != current_video_name:
            # 清除之前的结果
            st.session_state.current_video_name = current_video_name
            st.session_state.processed = False
            st.session_state.summary = None
            st.session_state.transcript = None
            st.session_state.slides = None
            st.session_state.video_info = None
            st.session_state.pdf_data = None

        # 显示视频信息
        from video import get_video_info

        try:
            video_info = get_video_info(video_path)
            st.session_state.video_info = video_info

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("时长", f"{video_info['duration']:.1f}秒")
            with col2:
                st.metric("分辨率", f"{video_info['width']}x{video_info['height']}")
            with col3:
                st.metric("帧率", f"{video_info['fps']:.1f}")
            with col4:
                st.metric("格式", video_info["format"].upper())

        except Exception as e:
            st.error(f"读取视频信息失败: {e}")
            return

        # 保存video_path到session state
        st.session_state.video_path = video_path

        # 检查是否已经处理过当前视频
        if (st.session_state.get("processed") and
            st.session_state.get("summary") and
            st.session_state.get("current_video_name") == current_video_name):
            # 显示已有结果
            display_results()
        else:
            # 处理步骤
            st.markdown("---")
            st.subheader("🔄 处理流程")

            # 检查API密钥
            provider = api_manager.get_provider()
            api_key = api_manager.get_api_key(provider)

            if not api_key:
                st.warning("⚠️ 请在侧边栏配置API密钥")

            # 处理按钮
            if st.button("🚀 开始处理", type="primary"):
                process_video(video_path, config)


def display_results():
    """显示处理结果"""
    # 显示视频信息
    if st.session_state.get("video_info"):
        video_info = st.session_state.video_info
        st.markdown("---")
        st.subheader("📹 视频信息")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("时长", f"{video_info['duration']:.1f}秒")
        with col2:
            st.metric("分辨率", f"{video_info['width']}x{video_info['height']}")
        with col3:
            st.metric("帧率", f"{video_info['fps']:.1f}")
        with col4:
            st.metric("格式", video_info["format"].upper())

    # 显示结果
    st.markdown("---")
    st.subheader("📝 总结结果")

    if st.session_state.summary:
        st.markdown(st.session_state.summary)

        # 导出按钮
        st.download_button(
            "📥 下载总结",
            st.session_state.summary,
            file_name="course_summary.md",
            type="primary",
        )

    # 下载转写按钮
    if st.session_state.get("transcript"):
        transcript_text = st.session_state.transcript.get("text", "")
        if transcript_text:
            st.download_button(
                "📥 下载转写",
                transcript_text,
                file_name="transcript.txt",
                mime="text/plain",
            )

    # 下载幻灯片文字按钮
    if st.session_state.get("slides"):
        slides_texts = []
        for slide in st.session_state.slides:
            if slide.get("text"):
                slides_texts.append(f"幻灯片 {slide.get('index', 0)+1}:\n{slide.get('text', '')}\n")

        if slides_texts:
            slides_content = "\n---\n".join(slides_texts)
            st.download_button(
                "📥 下载幻灯片文字",
                slides_content,
                file_name="slides_text.txt",
                mime="text/plain",
            )

        # 初始化PDF缓存
        if "pdf_data" not in st.session_state:
            st.session_state.pdf_data = None

        # 生成PDF按钮
        if st.session_state.pdf_data is None:
            if st.button("📥 生成幻灯片PDF"):
                with st.spinner("生成PDF中..."):
                    try:
                        from reportlab.lib.pagesizes import landscape, A4
                        from reportlab.pdfgen import canvas
                        from PIL import Image
                        import io

                        # 创建PDF
                        pdf_buffer = io.BytesIO()
                        c = canvas.Canvas(pdf_buffer, pagesize=landscape(A4))
                        width, height = landscape(A4)

                        project_root = Path(__file__).parent.parent

                        for i, slide in enumerate(st.session_state.slides):
                            img_path = slide.get("path", "")
                            if os.path.exists(img_path):
                                # 读取图片
                                img = Image.open(img_path)
                                if img:
                                    # 获取图片尺寸
                                    w, h = img.size
                                    # 计算缩放比例
                                    scale = min(width / w, height / h)
                                    new_w = int(w * scale * 0.9)
                                    new_h = int(h * scale * 0.9)
                                    # 计算居中位置
                                    x = (width - new_w) / 2
                                    y = (height - new_h) / 2

                                    # 保存临时图片
                                    temp_path = str(project_root / "temp" / f"temp_slide_{i}.jpg")
                                    img.save(temp_path)

                                    # 添加图片到PDF
                                    c.drawImage(temp_path, x, y, width=new_w, height=new_h)
                                    c.showPage()

                                    # 删除临时文件
                                    os.remove(temp_path)

                        c.save()
                        pdf_buffer.seek(0)
                        st.session_state.pdf_data = pdf_buffer.getvalue()
                        st.rerun()
                    except Exception as e:
                        st.error(f"PDF生成失败: {e}")

        # 如果PDF已生成，显示下载按钮
        if st.session_state.pdf_data:
            st.download_button(
                "📥 下载幻灯片PDF",
                st.session_state.pdf_data,
                file_name="slides.pdf",
                mime="application/pdf",
            )

    # 显示转写结果
    if st.session_state.get("show_transcript") and st.session_state.transcript:
        st.subheader("📝 转写文本")
        st.text_area(
            "转写文本",
            st.session_state.transcript["text"],
            height=300,
        )

    # 显示PPT
    if st.session_state.get("show_slides") and st.session_state.slides:
        st.subheader("📊 幻灯片")
        cols = st.columns(3)
        for i, slide in enumerate(st.session_state.slides):
            with cols[i % 3]:
                st.image(slide["path"], caption=f"幻灯片 {i+1}")
                if slide.get("text"):
                    st.caption(slide["text"][:100] + "...")


def process_video(video_path: str, config: dict):
    """处理视频"""
    st.session_state.processing = True

    # 使用绝对路径
    project_root = Path(__file__).parent.parent
    temp_dir = str(project_root / "temp")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Step 1: 音频提取
        with st.expander("Step 1: 提取音频", expanded=True):
            with st.spinner("提取音频中..."):
                audio_path = extract_audio(video_path, temp_dir)
                st.session_state.audio_path = audio_path
                st.success(f"✓ 音频已提取: {audio_path}")

        # Step 2: 语音转写
        with st.expander("Step 2: 语音转写", expanded=True):
            with st.spinner("语音转写中(首次运行需下载模型)..."):
                asr = WhisperASR(
                    model_size=config["whisper_model"],
                    device="cpu",
                )
                transcript_result = asr.transcribe_with_timestamps(audio_path)
                st.session_state.transcript = transcript_result
                st.success(f"✓ 转写完成，共 {len(transcript_result['segments'])} 个段落")

        # Step 3: PPT截取
        with st.expander("Step 3: PPT检测", expanded=True):
            with st.spinner("视频抽帧中..."):
                # 每秒抽一帧
                frames = extract_frames(video_path, temp_dir, interval=1.0)
                st.info(f"共提取 {len(frames)} 帧")

            with st.spinner("相似度检测中..."):
                slide_detector = SlideDetector(
                    similarity_threshold=config["similarity_threshold"]
                )
                unique_frames, _ = slide_detector.filter_similar_frames(frames)
                st.info(f"相似度过滤后: {len(unique_frames)} 张")

            with st.spinner("清晰度检测中..."):
                clarity_checker = ClarityChecker(
                    clarity_threshold=config["clarity_threshold"]
                )
                clear_frames, _ = clarity_checker.filter_blurry_frames(unique_frames)
                st.info(f"清晰度过滤后: {len(clear_frames)} 张")

            with st.spinner("OCR文字提取中..."):
                ocr_extractor = OCRExtractor()
                slides = ocr_extractor.extract_from_multiple(clear_frames)
                st.session_state.slides = slides
                st.success(f"✓ PPT提取完成，共 {len(slides)} 张")

        # Step 4: AI总结
        with st.expander("Step 4: AI总结", expanded=True):
            # 检查API密钥
            provider = api_manager.get_provider()
            api_key = api_manager.get_api_key(provider)

            if not api_key:
                st.error("请先配置API密钥")
                return

            with st.spinner("AI生成总结中..."):
                # 准备转写文本
                transcript_text = st.session_state.transcript["text"]

                # 准备幻灯片数据
                slides_data = [
                    {"text": s.get("text", ""), "time": s.get("time")}
                    for s in st.session_state.slides
                ]

                # 生成总结
                summarizer = CourseSummarizer()
                summary = summarizer.generate_summary(
                    transcript=transcript_text,
                    slides=slides_data,
                    title="课程总结",
                )
                st.session_state.summary = summary
                st.success("✓ 总结生成完成")

        # 初始化显示选项的session state
        if "show_transcript" not in st.session_state:
            st.session_state.show_transcript = False
        if "show_slides" not in st.session_state:
            st.session_state.show_slides = False

        # 显示结果
        st.markdown("---")
        st.subheader("📝 总结结果")

        if st.session_state.summary:
            st.markdown(st.session_state.summary)

            # 导出按钮
            st.download_button(
                "📥 下载总结",
                st.session_state.summary,
                file_name="course_summary.md",
                type="primary",
            )

        # 下载转写按钮
        if st.session_state.get("transcript"):
            transcript_text = st.session_state.transcript.get("text", "")
            if transcript_text:
                st.download_button(
                    "📥 下载转写",
                    transcript_text,
                    file_name="transcript.txt",
                    mime="text/plain",
                )

        # 下载幻灯片文字按钮
        if st.session_state.get("slides"):
            slides_texts = []
            for slide in st.session_state.slides:
                if slide.get("text"):
                    slides_texts.append(f"幻灯片 {slide.get('index', 0)+1}:\n{slide.get('text', '')}\n")

            if slides_texts:
                slides_content = "\n---\n".join(slides_texts)
                st.download_button(
                    "📥 下载幻灯片文字",
                    slides_content,
                    file_name="slides_text.txt",
                    mime="text/plain",
                )

            # 初始化PDF缓存
            if "pdf_data" not in st.session_state:
                st.session_state.pdf_data = None

            # 生成PDF按钮
            if st.session_state.pdf_data is None:
                if st.button("📥 生成幻灯片PDF"):
                    with st.spinner("生成PDF中..."):
                        try:
                            from reportlab.lib.pagesizes import landscape, A4
                            from reportlab.pdfgen import canvas
                            from PIL import Image
                            import io

                            # 创建PDF
                            pdf_buffer = io.BytesIO()
                            c = canvas.Canvas(pdf_buffer, pagesize=landscape(A4))
                            width, height = landscape(A4)

                            for i, slide in enumerate(st.session_state.slides):
                                img_path = slide.get("path", "")
                                if os.path.exists(img_path):
                                    # 读取图片
                                    img = Image.open(img_path)
                                    if img:
                                        # 获取图片尺寸
                                        w, h = img.size
                                        # 计算缩放比例
                                        scale = min(width / w, height / h)
                                        new_w = int(w * scale * 0.9)
                                        new_h = int(h * scale * 0.9)
                                        # 计算居中位置
                                        x = (width - new_w) / 2
                                        y = (height - new_h) / 2

                                        # 保存临时图片
                                        project_root = Path(__file__).parent.parent
                                        temp_path = str(project_root / "temp" / f"temp_slide_{i}.jpg")
                                        img.save(temp_path)

                                        # 添加图片到PDF
                                        c.drawImage(temp_path, x, y, width=new_w, height=new_h)
                                        c.showPage()

                                        # 删除临时文件
                                        os.remove(temp_path)

                            c.save()
                            pdf_buffer.seek(0)
                            st.session_state.pdf_data = pdf_buffer.getvalue()
                            st.rerun()
                        except Exception as e:
                            st.error(f"PDF生成失败: {e}")

            # 如果PDF已生成，显示下载按钮
            if st.session_state.pdf_data:
                st.download_button(
                    "📥 下载幻灯片PDF",
                    st.session_state.pdf_data,
                    file_name="slides.pdf",
                    mime="application/pdf",
                )

        # 显示转写结果
        if st.session_state.get("show_transcript") and st.session_state.transcript:
            st.subheader("📝 转写文本")
            st.text_area(
                "转写文本",
                st.session_state.transcript["text"],
                height=300,
            )

        # 显示PPT
        if st.session_state.get("show_slides") and st.session_state.slides:
            st.subheader("📊 幻灯片")
            cols = st.columns(3)
            for i, slide in enumerate(st.session_state.slides):
                with cols[i % 3]:
                    st.image(slide["path"], caption=f"幻灯片 {i+1}")
                    if slide.get("text"):
                        st.caption(slide["text"][:100] + "...")

    except Exception as e:
        st.error(f"处理失败: {e}")
        import traceback
        st.code(traceback.format_exc())

    finally:
        st.session_state.processing = False
        # 处理完成后标记
        if st.session_state.get("summary"):
            st.session_state.processed = True


def main():
    """主函数"""
    init_session_state()

    # 侧边栏配置
    config = sidebar_config()

    # 主页面
    main_page(config)


if __name__ == "__main__":
    main()
