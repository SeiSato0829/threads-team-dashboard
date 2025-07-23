@echo off
cd /d %~dp0
echo ================================================
echo   Quick Daily Auto Post Setup
echo   One-click setup for daily automation
echo ================================================
echo.

REM Install required packages
echo Installing required packages...
pip install --quiet selenium pyperclip

REM Create default config
echo Creating default configuration...
echo {
echo   "posts_per_day": 5,
echo   "posting_times": ["08:00", "12:00", "19:00", "21:00", "23:00"],
echo   "generate_days_ahead": 3,
echo   "retry_attempts": 3,
echo   "retry_delay": 300,
echo   "threads_login_url": "https://threads.net/login",
echo   "headless_mode": false,
echo   "execution_times": ["07:00", "11:00", "18:00", "20:00", "22:00"]
echo } > auto_post_config.json

REM Create credentials file
echo.
echo Setting up credentials...
echo {
echo   "username": "seisato0829",
echo   "password": "zx7bhh53"
echo } > threads_credentials.json

REM Create run batch
echo Creating execution batch file...
(
echo @echo off
echo cd /d %%~dp0
echo echo Running Daily Auto Post...
echo python DAILY_AUTO_POST_ENGINE.py --execute
echo exit
) > RUN_DAILY_POST.bat

REM Setup task scheduler
echo.
echo Setting up Windows Task Scheduler...
echo.

REM Delete existing tasks
schtasks /delete /tn "ThreadsAutoPost_1" /f 2>nul
schtasks /delete /tn "ThreadsAutoPost_2" /f 2>nul
schtasks /delete /tn "ThreadsAutoPost_3" /f 2>nul
schtasks /delete /tn "ThreadsAutoPost_4" /f 2>nul
schtasks /delete /tn "ThreadsAutoPost_5" /f 2>nul

REM Create tasks
schtasks /create /tn "ThreadsAutoPost_1" /tr "%cd%\RUN_DAILY_POST.bat" /sc daily /st 07:00 /f
schtasks /create /tn "ThreadsAutoPost_2" /tr "%cd%\RUN_DAILY_POST.bat" /sc daily /st 11:00 /f
schtasks /create /tn "ThreadsAutoPost_3" /tr "%cd%\RUN_DAILY_POST.bat" /sc daily /st 18:00 /f
schtasks /create /tn "ThreadsAutoPost_4" /tr "%cd%\RUN_DAILY_POST.bat" /sc daily /st 20:00 /f
schtasks /create /tn "ThreadsAutoPost_5" /tr "%cd%\RUN_DAILY_POST.bat" /sc daily /st 22:00 /f

echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo Daily auto posting is now configured:
echo - 5 posts per day at: 8:00, 12:00, 19:00, 21:00, 23:00
echo - Automatic execution at: 7:00, 11:00, 18:00, 20:00, 22:00
echo.
echo Test now? (y/n)
set /p test=
if /i "%test%"=="y" (
    echo.
    echo Running test execution...
    python DAILY_AUTO_POST_ENGINE.py --execute
)

echo.
pause