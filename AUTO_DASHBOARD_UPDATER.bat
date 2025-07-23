@echo off
cd /d %~dp0

:loop
echo %date% %time% - Updating dashboard data...

REM データベースの整合性チェック
python -c "
import sqlite3
import os
from datetime import datetime

# データベースファイルの確認と更新
dbs = ['scheduled_posts.db', 'threads_optimized.db', 'buzz_history.db', 'viral_history.db']
for db in dbs:
    if os.path.exists(db):
        try:
            conn = sqlite3.connect(db)
            conn.execute('SELECT COUNT(*) FROM sqlite_master')
            conn.close()
            print(f'✅ {db} OK')
        except:
            print(f'❌ {db} Error')
    else:
        print(f'ℹ️ {db} Not found')

print(f'Last update: {datetime.now().strftime("%Y/%m/%d %H:%M:%S")}')
"

timeout /t 300 /nobreak
goto loop
