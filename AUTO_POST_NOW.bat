@echo off
cd /d %~dp0

echo ========================================
echo   完全自動投稿予約システム
echo ========================================
echo.

echo Step 1: 投稿を生成中...
python -c "from simple_auto_post import generate_simple_post, save_to_schedule; import json; posts = []; print('5件の投稿を生成中...'); [posts.append(save_to_schedule(generate_simple_post())) for _ in range(5)]; print('生成完了！')"

echo.
echo Step 2: Bufferに予約投稿中...
python auto_post_to_buffer.py

pause