@echo off
cd /d "%~dp0"

echo Starting Threads Dashboard...

echo Step 1: Installing required libraries...
python -m pip install streamlit plotly pandas qrcode[pil] --quiet
if %ERRORLEVEL% NEQ 0 (
    pip install streamlit plotly pandas qrcode[pil] --quiet
)

echo Step 2: Checking system...
if not exist "CLOUD_SHARE_DASHBOARD.py" (
    echo ERROR: CLOUD_SHARE_DASHBOARD.py not found
    pause
    exit /b 1
)

echo Step 3: Starting dashboard...
echo Trying to start on available port...
echo.

python -m streamlit run CLOUD_SHARE_DASHBOARD.py --server.port=8502 --server.address=0.0.0.0
if %ERRORLEVEL% NEQ 0 (
    echo Trying alternative port...
    python -m streamlit run CLOUD_SHARE_DASHBOARD.py --server.port=8503 --server.address=0.0.0.0
    if %ERRORLEVEL% NEQ 0 (
        echo Trying port 8504...
        streamlit run CLOUD_SHARE_DASHBOARD.py --server.port=8504 --server.address=0.0.0.0
    )
)

echo Dashboard stopped
pause
