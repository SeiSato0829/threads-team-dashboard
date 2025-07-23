@echo off
cd /d %~dp0
echo ================================================
echo   Buzz Post Daily Setup
echo   Setup automatic viral buzz posting
echo ================================================
echo.

REM Install required packages
echo Installing required packages...
pip install --quiet selenium pyperclip

REM Create buzz config
echo Creating buzz configuration...
echo {
echo   "posts_per_day": 5,
echo   "posting_times": ["09:00", "12:00", "19:00", "21:00", "23:00"],
echo   "generate_days_ahead": 3,
echo   "retry_attempts": 3,
echo   "retry_delay": 300,
echo   "threads_login_url": "https://threads.net/login",
echo   "headless_mode": false,
echo   "execution_times": ["09:00", "12:00", "19:00", "21:00", "23:00"],
echo   "use_buzz_engine": true,
echo   "engine_type": "viral_buzz"
echo } > auto_post_config.json

REM Create credentials
echo.
echo Setting up credentials...
echo {
echo   "username": "seisato0829",
echo   "password": "zx7bhh53"
echo } > threads_credentials.json

REM Create buzz run batch
echo Creating buzz execution batch...
(
echo @echo off
echo cd /d %%~dp0
echo echo Running Buzz Auto Post...
echo python BUZZ_DAILY_RUNNER.py
echo exit
) > RUN_BUZZ_POST.bat

REM Create runner script
echo Creating runner script...
(
echo import asyncio
echo import sys
echo sys.path.insert(0, '.')
echo from VIRAL_BUZZ_ENGINE import BuzzViralEngine
echo from DAILY_AUTO_POST_ENGINE import DailyAutoPostEngine
echo 
echo class BuzzDailyEngine(DailyAutoPostEngine^):
echo     def __init__(self^):
echo         super(^).__init__(^)
echo         self.ai_engine = BuzzViralEngine(^)
echo 
echo async def main(^):
echo     engine = BuzzDailyEngine(^)
echo     await engine.daily_execution(^)
echo 
echo if __name__ == "__main__":
echo     asyncio.run(main(^)^)
) > BUZZ_DAILY_RUNNER.py

REM Setup task scheduler
echo.
echo Setting up Windows Task Scheduler for buzz posts...
echo.

REM Delete existing tasks
schtasks /delete /tn "BuzzPost_1" /f 2>nul
schtasks /delete /tn "BuzzPost_2" /f 2>nul
schtasks /delete /tn "BuzzPost_3" /f 2>nul
schtasks /delete /tn "BuzzPost_4" /f 2>nul
schtasks /delete /tn "BuzzPost_5" /f 2>nul

REM Create buzz tasks
schtasks /create /tn "BuzzPost_1" /tr "%cd%\RUN_BUZZ_POST.bat" /sc daily /st 09:00 /f
schtasks /create /tn "BuzzPost_2" /tr "%cd%\RUN_BUZZ_POST.bat" /sc daily /st 12:00 /f
schtasks /create /tn "BuzzPost_3" /tr "%cd%\RUN_BUZZ_POST.bat" /sc daily /st 19:00 /f
schtasks /create /tn "BuzzPost_4" /tr "%cd%\RUN_BUZZ_POST.bat" /sc daily /st 21:00 /f
schtasks /create /tn "BuzzPost_5" /tr "%cd%\RUN_BUZZ_POST.bat" /sc daily /st 23:00 /f

echo.
echo ================================================
echo   Buzz Setup Complete!
echo ================================================
echo.
echo Daily buzz posting is now configured:
echo - 5 viral buzz posts per day
echo - Natural word-of-mouth style
echo - No emojis, authentic feel
echo - Automatic execution at: 9:00, 12:00, 19:00, 21:00, 23:00
echo.
echo Test now? (y/n)
set /p test=
if /i "%test%"=="y" (
    echo.
    echo Generating test buzz posts...
    python BUZZ_SYSTEM.py
)

echo.
pause