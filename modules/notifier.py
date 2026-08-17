"""
modules/notifier.py
------------------------------------
Telegram Notification Engine
"""

import requests
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "banking.db"

# TODO: Thay thế bằng Token Bot thật của bạn lấy từ @BotFather
TELEGRAM_BOT_TOKEN = "8937286868:AAGP15wztbgcPlWFyhHii3vRUGwNp39hnPY"

class Notifier:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    def get_fraud_team_chat_ids(self):
        """Lấy danh sách Telegram Chat ID của tất cả nhân sự có Role là FRAUD"""
        cur = self.conn.cursor()
        cur.execute("SELECT TELEGRAM_ID FROM USERS WHERE ROLE='FRAUD' AND TELEGRAM_ID IS NOT NULL")
        rows = cur.fetchall()
        return [row[0] for row in rows if row[0].strip() != ""]

    def notify_fraud_team(self, case_id, old_status, new_status, updater_email):
        """Gửi tin nhắn thông báo cập nhật Case đến toàn bộ team FRAUD"""
        chat_ids = self.get_fraud_team_chat_ids()
        
        if not chat_ids:
            return {"status": False, "message": "Không tìm thấy Telegram ID của team FRAUD."}

        message = (
            f"🚨 **FRAUD PORTAL NOTIFICATION** 🚨\n\n"
            f"📂 **Case ID:** `{case_id}`\n"
            f"🔄 **Trạng thái:** `{old_status}` ➡️ `{new_status}`\n"
            f"👤 **Cập nhật bởi KSV:** {updater_email}\n\n"
            f"👉 Vui lòng truy cập [Fraud Case Management Portal] để kiểm tra và xử lý."
        )

        success_count = 0
        for chat_id in chat_ids:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            try:
                res = requests.post(url, json=payload)
                if res.status_code == 200:
                    success_count += 1
            except Exception as e:
                pass # Bỏ qua nếu lỗi mạng

        return {"status": True, "message": f"Đã gửi thông báo tới {success_count} nhân sự FRAUD."}

    def close(self):
        self.conn.close()