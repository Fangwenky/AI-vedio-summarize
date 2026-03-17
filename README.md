# AI课程录播总结工具

一个本地运行的AI课程视频 summarization 工具，支持：视频上传、语音转写、PPT画面截取、AI智能总结。

## 功能特性

- 📹 **视频上传** - 支持MP4、AVI、MOV、MKV格式
- 🎙️ **语音转写** - 使用Whisper本地模型进行语音识别
- 📊 **PPT检测** - 自动提取幻灯片并进行OCR文字识别
- 🤖 **AI总结** - 支持多服务商的LLM API进行智能总结

## 技术栈

- **后端核心**: Python 3.10+
- **前端框架**: Streamlit
- **视频处理**: ffmpeg-python, OpenCV
- **语音识别**: openai-whisper
- **OCR**: pytesseract
- **LLM调用**: OpenAI/Claude/Qwen/MiniMax

## 项目结构

```
AI-vedio-summarize/
├── config/          # 配置模块
│   ├── settings.py  # 全局配置
│   └── api_manager.py  # API密钥管理
├── video/          # 视频处理模块
│   ├── video_processor.py
│   ├── audio_extractor.py
│   └── frame_extractor.py
├── ppt/            # PPT检测模块
│   ├── slide_detector.py
│   ├── clarity_checker.py
│   └── ocr_extractor.py
├── asr/            # 语音转写模块
│   ├── whisper_asr.py
│   └── timestamp_aligner.py
├── llm/            # AI总结模块
│   ├── llm_client.py
│   └── summarizer.py
├── ui/             # 前端界面
│   └── app.py
└── requirements.txt
```

## 安装

1. 安装Python依赖:
```bash
pip install -r requirements.txt
```

2. 安装ffmpeg:
   - Windows: 下载并安装ffmpeg
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

3. 安装Tesseract OCR:
   - Windows: 下载并安装Tesseract
   - macOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

## 使用方法

1. 启动应用:
```bash
streamlit run ui/app.py
```

2. 在浏览器中打开 http://localhost:8501

3. 在侧边栏配置:
   - 选择LLM服务商(OpenAI/Claude/Qwen/MiniMax)
   - 输入API密钥

4. 上传视频文件，点击"开始处理"

## 配置说明

### 支持的LLM服务商

- **OpenAI**: gpt-4o, gpt-4o-mini, gpt-4-turbo
- **Anthropic Claude**: claude-3-5-sonnet, claude-3-opus
- **阿里Qwen**: qwen-turbo, qwen-plus, qwen-max
- **MiniMax**: abab6.5s-chat, abab6.5g-chat

### Whisper模型

- tiny: ~39MB, 最快, 精度较低
- base: ~74MB, 推荐日常使用
- small: ~244MB
- medium: ~769MB
- large: ~1550MB, 最高精度

## 注意事项

- Whisper首次运行需要下载模型(约500MB)
- API密钥本地加密存储
- 处理长视频可能需要较长时间

## 许可证

MIT License
