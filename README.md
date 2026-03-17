# AI课程录播总结工具

一个本地运行的AI课程视频 summarization 工具，支持：视频上传、语音转写、PPT画面截取、AI智能总结。

## 功能特性

- 📹 **视频上传** - 支持上传或本地路径输入，支持MP4、AVI、MOV、MKV格式
- 🎙️ **语音转写** - 使用Whisper本地模型进行语音识别
- 📊 **PPT检测** - 自动提取幻灯片，相似度去重，清晰度过滤，OCR文字识别
- 🤖 **AI总结** - 支持多服务商的LLM API进行智能总结
- 📥 **多种下载** - 支持下载总结、转写文本、幻灯片文字、幻灯片PDF

## 技术栈

- **后端核心**: Python 3.10+
- **前端框架**: Streamlit
- **视频处理**: ffmpeg-python, OpenCV
- **语音识别**: openai-whisper
- **OCR**: pytesseract
- **PDF生成**: reportlab
- **LLM调用**: OpenAI/Claude/Qwen/MiniMax

## 项目结构

```
AI-vedio-summarize/
├── config/              # 配置模块
│   ├── settings.py     # 全局配置
│   └── api_manager.py  # API密钥管理
├── video/              # 视频处理模块
│   ├── video_processor.py  # 视频信息获取
│   ├── audio_extractor.py   # 音频提取
│   └── frame_extractor.py   # 视频抽帧
├── ppt/                # PPT检测模块
│   ├── slide_detector.py    # 相似度检测(SSIM)
│   ├── clarity_checker.py   # 清晰度检测(Laplacian)
│   └── ocr_extractor.py     # OCR文字提取
├── asr/                # 语音转写模块
│   ├── whisper_asr.py       # Whisper转写
│   └── timestamp_aligner.py # 时间戳对齐
├── llm/                # AI总结模块
│   ├── llm_client.py      # 通用LLM客户端
│   └── summarizer.py      # 课程总结生成
├── ui/                 # 前端界面
│   └── app.py           # Streamlit主界面
├── .streamlit/         # Streamlit配置
├── .gitignore
├── requirements.txt
└── README.md
```

## 安装

1. 克隆项目并进入目录:
```bash
cd AI-vedio-summarize
```

2. 安装Python依赖:
```bash
pip install -r requirements.txt
```

3. 安装ffmpeg:
   - Windows: 使用winget `winget install ffmpeg` 或下载安装
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

4. 安装Tesseract OCR:
   - Windows: 下载并安装Tesseract
   - macOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

## 使用方法

1. 启动应用:
```bash
streamlit run ui/app.py
```

2. 在浏览器中打开 http://localhost:8501

3. 侧边栏配置:
   - 选择LLM服务商 (OpenAI/Claude/Qwen/MiniMax)
   - 输入API密钥
   - (可选) 调整PPT检测参数

4. 选择视频输入方式:
   - 上传视频文件
   - 或输入本地视频路径

5. 点击"开始处理"

6. 处理完成后可:
   - 查看AI生成的课程总结
   - 显示/隐藏转写文本
   - 显示/隐藏幻灯片
   - 下载总结、转写、幻灯片文字、PDF

## 配置说明

### 支持的LLM服务商

| 服务商 | 模型 |
|--------|------|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-4-turbo |
| Anthropic Claude | claude-3-5-sonnet, claude-3-opus |
| 阿里Qwen | qwen-turbo, qwen-plus, qwen-max |
| MiniMax | MiniMax-M2.5, MiniMax-M2.5-highspeed, MiniMax-M2.1 |

### MiniMax配置说明

MiniMax Coding Plan用户需要:
- API密钥 (sk-cp-xxx格式)
- 模型选择 "MiniMax-M2.5"

### Whisper模型

| 模型 | 大小 | 推荐场景 |
|------|------|----------|
| tiny | ~39MB | 快速测试 |
| base | ~74MB | 推荐日常使用 |
| small | ~244MB | 平衡速度和精度 |
| medium | ~769MB | 较高精度 |
| large | ~1550MB | 最高精度 |

### PPT检测参数

- **相似度阈值**: 0.7-0.99，值越高越容易识别为不同幻灯片
- **清晰度阈值**: 50-200，值越高对图片清晰度要求越高

## 注意事项

- Whisper首次运行需要下载模型(约500MB)
- API密钥本地加密存储，刷新页面后自动加载
- 处理长视频可能需要较长时间
- 生成的临时文件保存在 `temp/` 目录
- 上传新视频会自动清除之前的结果

## 许可证

MIT License
