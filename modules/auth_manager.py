import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "banking.db"

class AuthManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_table()
        self.seed_admin()

    def create_table(self):
        # 1. Kiểm tra xem bảng USERS hiện tại có cột EMAIL hay chưa
        try:
            self.conn.execute("SELECT EMAIL FROM USERS LIMIT 1")
        except sqlite3.OperationalError:
            # 2. Nếu báo lỗi (tức là đang dùng bảng cũ), ta sẽ xóa bảng cũ đi
            self.conn.execute("DROP TABLE IF EXISTS USERS")

        # 3. Tạo lại bảng với cấu trúc hoàn toàn mới
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS USERS (
            EMAIL TEXT PRIMARY KEY,
            ROLE TEXT,
            TELEGRAM_ID TEXT
        )
        """)
        self.conn.commit()

    def seed_admin(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM USERS WHERE EMAIL='admin@bank.com'")
        if not cur.fetchone():
            self.conn.execute(
                "INSERT INTO USERS (EMAIL, ROLE, TELEGRAM_ID) VALUES (?, ?, ?)",
                ("admin@bank.com", "SYSTEM ADMIN", "")
            )
            self.conn.commit()

    def authenticate_by_email(self, email):
        """Hàm này mô phỏng việc sau khi Google OAuth trả về Email thành công"""
        cur = self.conn.cursor()
        cur.execute("SELECT ROLE FROM USERS WHERE EMAIL=?", (email,))
        user = cur.fetchone()
        if user:
            return {"status": True, "role": user[0]}
        return {"status": False, "message": "Email này chưa được System Admin cấp quyền truy cập."}

    def create_user(self, email, role, telegram_id=""):
        try:
            self.conn.execute(
                "INSERT INTO USERS (EMAIL, ROLE, TELEGRAM_ID) VALUES (?, ?, ?)",
                (email, role, telegram_id)
            )
            self.conn.commit()
            return {"status": True, "message": f"Tạo user {email} thành công."}
        except sqlite3.IntegrityError:
            return {"status": False, "message": "Email này đã tồn tại trong hệ thống."}

    def get_all_users(self):
        return pd.read_sql_query("SELECT EMAIL, ROLE, TELEGRAM_ID FROM USERS", self.conn)