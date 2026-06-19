@echo off
cd /d "%~dp0"
call myenv\Scripts\activate
python -m streamlit run app.py --server.port 8501 --server.headless true
