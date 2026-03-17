@echo off
set KMP_DUPLICATE_LIB_OK=TRUE
start "Streamlit" cmd /c "python -m streamlit run D:\Develop\Project\AI-vedio-summarize\ui\app.py --server.port 8501"
