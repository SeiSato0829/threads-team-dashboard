@echo off
cd /d %~dp0
pip install streamlit
python simple_auto_post.py
pause