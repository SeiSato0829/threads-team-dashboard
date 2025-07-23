#!/usr/bin/env python3
"""
一括スケジュール投稿フォーマッター
1回のコピペで複数投稿を時間指定付きで管理
"""

import csv
import json
from datetime import datetime, timedelta
import os

class BatchScheduleFormatter:
    def __init__(self):
        # デフォルトの投稿時間（6つの時間帯）
        self.default_times = [
            "07:30",  # 早朝
            "09:00",  # 朝
            "12:00",  # 昼
            "15:00",  # 午後
            "18:00",  # 夕方
            "21:00"   # 夜
        ]
    
    def create_batch_format(self, posts, days=5, output_format='multi'):
        """
        投稿を指定日数・時間に振り分けて特殊フォーマットで出力
        
        Args:
            posts: 投稿内容のリスト
            days: 振り分ける日数
            output_format: 'multi' (複数行形式) or 'single' (1行形式)
        """
        
        scheduled_posts = []
        base_date = datetime.now()
        posts_per_day = 6  # 1日6投稿
        
        post_index = 0
        
        for day in range(days):
            current_date = base_date + timedelta(days=day)
            
            for time_str in self.default_times:
                if post_index >= len(posts):
                    break
                    
                hour, minute = map(int, time_str.split(':'))
                post_time = current_date.replace(hour=hour, minute=minute)
                
                scheduled_posts.append({
                    'datetime': post_time,
                    'date': post_time.strftime('%Y/%m/%d'),
                    'time': time_str,
                    'content': posts[post_index],
                    'index': post_index + 1
                })
                
                post_index += 1
        
        if output_format == 'multi':
            return self._format_multi_line(scheduled_posts)
        else:
            return self._format_single_line(scheduled_posts)
    
    def _format_multi_line(self, scheduled_posts):
        """
        複数行形式（Threads公式アプリの予約投稿用）
        各投稿を時間付きで個別の行に
        """
        output_lines = []
        
        for post in scheduled_posts:
            # 時間情報を先頭に付けた形式
            formatted_line = f"[{post['date']} {post['time']}] {post['content']}"
            output_lines.append(formatted_line)
        
        return '\n'.join(output_lines)
    
    def _format_single_line(self, scheduled_posts):
        """
        1行形式（特殊区切り文字使用）
        全投稿を1行にまとめてコピペ
        """
        # 特殊な区切り文字
        delimiter = " ||| "
        
        formatted_posts = []
        for post in scheduled_posts:
            # 時間と内容を結合
            formatted = f"{post['date']}_{post['time']}_{post['content']}"
            formatted_posts.append(formatted)
        
        return delimiter.join(formatted_posts)
    
    def create_spreadsheet_format(self, posts, days=5):
        """
        Googleスプレッドシート用の特殊フォーマット
        """
        scheduled_posts = self._schedule_posts(posts, days)
        
        # タブ区切り形式（スプレッドシートに直接貼り付け可能）
        output_lines = []
        
        # ヘッダー
        output_lines.append("日付\t時間\t投稿内容\tステータス\t投稿ID")
        
        for post in scheduled_posts:
            line = f"{post['date']}\t{post['time']}\t{post['content']}\t未投稿\t{post['index']}"
            output_lines.append(line)
        
        return '\n'.join(output_lines)
    
    def _schedule_posts(self, posts, days):
        """投稿をスケジュールに振り分け"""
        scheduled_posts = []
        base_date = datetime.now()
        post_index = 0
        
        for day in range(days):
            current_date = base_date + timedelta(days=day)
            
            for time_str in self.default_times:
                if post_index >= len(posts):
                    break
                    
                hour, minute = map(int, time_str.split(':'))
                post_time = current_date.replace(hour=hour, minute=minute)
                
                scheduled_posts.append({
                    'datetime': post_time,
                    'date': post_time.strftime('%Y/%m/%d'),
                    'time': time_str,
                    'content': posts[post_index],
                    'index': post_index + 1
                })
                
                post_index += 1
        
        return scheduled_posts
    
    def create_json_format(self, posts, days=5):
        """
        JSON形式（自動化ツール連携用）
        """
        scheduled_posts = self._schedule_posts(posts, days)
        
        json_data = {
            'generated_at': datetime.now().isoformat(),
            'total_posts': len(scheduled_posts),
            'schedule': []
        }
        
        for post in scheduled_posts:
            json_data['schedule'].append({
                'id': post['index'],
                'date': post['date'],
                'time': post['time'],
                'datetime_iso': post['datetime'].isoformat(),
                'content': post['content'],
                'hashtags': self._extract_hashtags(post['content']),
                'status': 'scheduled'
            })
        
        return json.dumps(json_data, ensure_ascii=False, indent=2)
    
    def _extract_hashtags(self, content):
        """投稿内容からハッシュタグを抽出"""
        import re
        hashtags = re.findall(r'#\w+', content)
        return hashtags
    
    def save_all_formats(self, posts, base_filename='batch_schedule'):
        """全ての形式でファイルを保存"""
        
        # 保存ディレクトリ
        os.makedirs('batch_schedules', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. 複数行形式
        multi_filename = f'batch_schedules/{base_filename}_multi_{timestamp}.txt'
        with open(multi_filename, 'w', encoding='utf-8') as f:
            f.write(self.create_batch_format(posts, output_format='multi'))
        
        # 2. 1行形式
        single_filename = f'batch_schedules/{base_filename}_single_{timestamp}.txt'
        with open(single_filename, 'w', encoding='utf-8') as f:
            f.write(self.create_batch_format(posts, output_format='single'))
        
        # 3. スプレッドシート形式
        sheet_filename = f'batch_schedules/{base_filename}_sheet_{timestamp}.tsv'
        with open(sheet_filename, 'w', encoding='utf-8') as f:
            f.write(self.create_spreadsheet_format(posts))
        
        # 4. JSON形式
        json_filename = f'batch_schedules/{base_filename}_data_{timestamp}.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            f.write(self.create_json_format(posts))
        
        return {
            'multi': multi_filename,
            'single': single_filename,
            'sheet': sheet_filename,
            'json': json_filename
        }


# 使用例
def demo():
    """デモ実行"""
    
    # サンプル投稿（30件）
    sample_posts = [
        "おはようございます！今日も素晴らしい1日の始まりです ☀️ #朝活",
        "生産性を上げるコツ：タスクを3つに絞ること 📝 #仕事術",
        "ランチタイムは脳をリフレッシュする大切な時間 🍽️",
        "午後の集中力を保つには、15分の仮眠が効果的 😴",
        "1日の振り返りが明日の成長につながる 📊 #成長",
        "今日も1日お疲れ様でした！ゆっくり休んでくださいね 🌙",
        # ... 続く（実際は30件）
    ] * 5  # デモ用に5倍に
    
    formatter = BatchScheduleFormatter()
    
    # 各形式で出力
    print("=== 複数行形式（予約投稿用）===")
    print(formatter.create_batch_format(sample_posts[:12], days=2, output_format='multi'))
    print("\n")
    
    print("=== スプレッドシート形式 ===")
    print(formatter.create_spreadsheet_format(sample_posts[:12], days=2))
    print("\n")
    
    # ファイルに保存
    saved_files = formatter.save_all_formats(sample_posts[:30])
    print("=== 保存されたファイル ===")
    for format_type, filename in saved_files.items():
        print(f"{format_type}: {filename}")


if __name__ == "__main__":
    demo()