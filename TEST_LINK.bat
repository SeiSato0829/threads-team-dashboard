@echo off
cd /d %~dp0
echo ================================================
echo   Link Inclusion Test
echo   Testing if the specified link is added to all posts
echo ================================================
echo.
python TEST_LINK_INCLUSION.py
pause