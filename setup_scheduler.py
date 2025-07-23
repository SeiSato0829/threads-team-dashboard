#!/usr/bin/env python3
"""
🕐 自動スケジューラー設定ツール
Windowsタスクスケジューラーで定期実行を設定
"""

import os
import sys
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def create_task_xml(task_name, script_path, schedule_time="09:00"):
    """タスクスケジューラー用XMLファイル作成"""
    
    # 現在のユーザー名を取得
    username = os.environ.get('USERNAME', 'User')
    
    xml_template = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().isoformat()}</Date>
    <Author>{username}</Author>
    <Description>Threads自動投稿システムの定期実行</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{datetime.now().strftime('%Y-%m-%d')}T{schedule_time}:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{username}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{script_path}</Command>
      <WorkingDirectory>{os.path.dirname(script_path)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
    
    return xml_template

def setup_windows_scheduler():
    """Windowsタスクスケジューラー設定"""
    print("""
    ╔════════════════════════════════════════════════════╗
    ║  🕐 自動スケジューラー設定                         ║
    ║     毎日決まった時間に完全自動化システムを実行     ║
    ╚════════════════════════════════════════════════════╝
    """)
    
    # 現在のディレクトリ取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # バッチファイルパス
    batch_file = os.path.join(current_dir, "auto_threads_scheduler.bat")
    
    # バッチファイル作成
    batch_content = f"""@echo off
chcp 65001 >nul
cd /d "{current_dir}"

echo 🚀 Threads完全自動化システムを開始...
echo 時刻: %date% %time%

python FULLY_AUTOMATED_SYSTEM.py --auto-run

if %errorlevel% neq 0 (
    echo ❌ エラーが発生しました
    echo エラーログを確認してください: threads_automation.log
) else (
    echo ✅ 自動化完了
)

echo.
echo ログファイル: threads_automation.log
"""
    
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"✅ バッチファイルを作成: {batch_file}")
    
    # タスク名
    task_name = "ThreadsAutoPosting"
    
    # 実行時間設定
    print(f"\n⏰ 毎日の実行時間を設定してください:")
    schedule_time = input("実行時間 (HH:MM形式, 例: 09:00): ").strip()
    if not schedule_time:
        schedule_time = "09:00"
    
    # XML設定ファイル作成
    xml_content = create_task_xml(task_name, batch_file, schedule_time)
    xml_file = f"{task_name}.xml"
    
    with open(xml_file, 'w', encoding='utf-16') as f:
        f.write(xml_content)
    
    print(f"✅ タスク設定ファイルを作成: {xml_file}")
    
    # タスクスケジューラーに登録
    print(f"\n📝 Windowsタスクスケジューラーに登録中...")
    
    try:
        # 既存のタスクを削除（存在する場合）
        subprocess.run(f'schtasks /delete /tn "{task_name}" /f', 
                      shell=True, capture_output=True)
        
        # 新しいタスクを作成
        result = subprocess.run(f'schtasks /create /xml "{xml_file}" /tn "{task_name}"',
                               shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"🎉 タスクスケジューラーに正常に登録されました!")
            print(f"📅 毎日 {schedule_time} に自動実行されます")
            print(f"📝 タスク名: {task_name}")
            
            # 登録状況確認
            check_result = subprocess.run(f'schtasks /query /tn "{task_name}"',
                                        shell=True, capture_output=True, text=True)
            if check_result.returncode == 0:
                print("✅ タスクが正常に登録されていることを確認しました")
            
        else:
            print(f"❌ タスクスケジューラーへの登録に失敗しました")
            print(f"エラー: {result.stderr}")
            print(f"\n手動で登録する場合:")
            print(f"1. Windowsキー + R → 'taskschd.msc' を実行")
            print(f"2. 「タスクの作成」をクリック")
            print(f"3. 「タスクのインポート」で {xml_file} を選択")
            
    except Exception as e:
        print(f"❌ タスクスケジューラー設定エラー: {e}")
    
    # クリーンアップ
    try:
        os.remove(xml_file)
        print(f"🧹 一時ファイルを削除: {xml_file}")
    except:
        pass
    
    print(f"\n🎯 設定完了!")
    print(f"📂 作業ディレクトリ: {current_dir}")
    print(f"🔧 バッチファイル: {batch_file}")
    print(f"📋 ログファイル: threads_automation.log")
    
    print(f"\n📋 手動実行したい場合:")
    print(f"   {batch_file} をダブルクリック")
    
    print(f"\n⚙️ タスク管理:")
    print(f"   有効化: schtasks /change /tn \"{task_name}\" /enable")
    print(f"   無効化: schtasks /change /tn \"{task_name}\" /disable")
    print(f"   削除: schtasks /delete /tn \"{task_name}\" /f")

def main():
    """メイン実行"""
    # 管理者権限チェック
    try:
        # 管理者権限が必要な処理をテスト
        subprocess.run('net session', shell=True, check=True, 
                      capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️ 管理者権限が必要です")
        print("右クリック → 「管理者として実行」でこのスクリプトを実行してください")
        input("\nEnterキーを押して終了...")
        return
    
    setup_windows_scheduler()
    
    print(f"\n✨ 完全自動化システムの準備が整いました!")
    input("\nEnterキーを押して終了...")

if __name__ == "__main__":
    main()