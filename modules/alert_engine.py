"""
modules/alert_engine.py
------------------------------------
Fraud Alert Engine
"""

import sqlite3
from pathlib import Path
from datetime import datetime

from modules.rule_engine import RuleEngine

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "banking.db"


class AlertEngine:

    def __init__(self):

        self.rule_engine = RuleEngine()

        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

        self.create_alert_table()

    # ==========================================
    # Create Alert Table
    # ==========================================

    def create_alert_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ALERT(
            ALERT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TXN_ID TEXT,
            CUSTOMER_ID TEXT,
            ALERT_LEVEL TEXT,
            RULE_SCORE INTEGER,
            STATUS TEXT,
            CREATED_TIME TEXT
        )
        """)

        self.conn.commit()

    # ==========================================
    # Alert Level Logic
    # ==========================================

    def alert_level(self, score):
        """
        Phân loại mức độ cảnh báo dựa trên điểm rủi ro.
        Dưới 40: LOW, 40-59: MEDIUM, 60-79: HIGH, >=80: CRITICAL
        """
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        return "LOW"

    # ==========================================
    # System Decision Logic
    # ==========================================

    def get_decision_from_level(self, level):
        """
        Hành động đề xuất từ hệ thống (System Decision).
        """
        mapping = {
            "LOW": "APPROVED",
            "MEDIUM": "REVIEWED",
            "HIGH": "REVIEWED",
            "CRITICAL": "BLOCKED"
        }
        return mapping.get(level, "REVIEWED")

    # ==========================================
    # Check Existing Alert
    # ==========================================

    def alert_exists(self, txn_id):

        self.cursor.execute("""
            SELECT ALERT_ID
            FROM ALERT
            WHERE TXN_ID=?
        """, (txn_id,))

        return self.cursor.fetchone() is not None

    # ==========================================
    # Generate Alert
    # ==========================================

    def generate_alert(self, txn_id):

        result = self.rule_engine.evaluate(txn_id)

        if not result["status"]:
            return result

        score = result["rule_score"]
        level = self.alert_level(score)
        
        # Quyết định hành động (Approve/Review/Block)
        decision = self.get_decision_from_level(level)

        # Trạng thái vòng đời (Status): < 40 là CLOSED, còn lại là OPEN để chờ xử lý
        alert_status = "CLOSED" if score < 40 else "OPEN"

        if self.alert_exists(txn_id):
            return {
                "status": True,
                "message": "Alert already exists."
            }

        self.cursor.execute("""
            INSERT INTO ALERT(
                TXN_ID,
                CUSTOMER_ID,
                ALERT_LEVEL,
                RULE_SCORE,
                STATUS,
                CREATED_TIME
            )
            VALUES(?,?,?,?,?,?)
        """, (
            result["transaction_id"],
            result["customer_id"],
            level,
            score,
            alert_status, # Ghi chuẩn OPEN hoặc CLOSED vào DB
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        self.conn.commit()

        return {
            "status": True,
            "transaction_id": result["transaction_id"],
            "customer_id": result["customer_id"],
            "alert_level": level,
            "rule_score": score,
            "decision": decision,         # Trả về quyết định hệ thống để UI hiển thị
            "alert_status": alert_status, # Trả về trạng thái ticket (OPEN/CLOSED)
            "triggered_rules": result["triggered_rules"]
        }

    # ==========================================
    # Get All Alerts
    # ==========================================

    def get_alerts(self):

        self.cursor.execute("""
            SELECT *
            FROM ALERT
            ORDER BY ALERT_ID DESC
        """)

        rows = self.cursor.fetchall()

        return [dict(r) for r in rows]

    # ==========================================
    # Get Alert
    # ==========================================

    def get_alert(self, alert_id):

        # Hỗ trợ lấy bằng ALERT_ID hoặc TXN_ID nếu người dùng truyền nhầm TXN_ID
        if str(alert_id).startswith("TXN"):
            self.cursor.execute("SELECT * FROM ALERT WHERE TXN_ID=?", (alert_id,))
        else:
            self.cursor.execute("SELECT * FROM ALERT WHERE ALERT_ID=?", (alert_id,))

        row = self.cursor.fetchone()

        if row:
            return dict(row)

        return None

    # ==========================================
    # Close Alert
    # ==========================================

    def close_alert(self, alert_id):

        self.cursor.execute("""
            UPDATE ALERT
            SET STATUS='CLOSED'
            WHERE ALERT_ID=?
        """, (alert_id,))

        self.conn.commit()

    # ==========================================
    # Reopen Alert
    # ==========================================

    def reopen_alert(self, alert_id):

        self.cursor.execute("""
            UPDATE ALERT
            SET STATUS='OPEN'
            WHERE ALERT_ID=?
        """, (alert_id,))

        self.conn.commit()

    # ==========================================
    # Delete Alert
    # ==========================================

    def delete_alert(self, alert_id):

        self.cursor.execute("""
            DELETE
            FROM ALERT
            WHERE ALERT_ID=?
        """, (alert_id,))

        self.conn.commit()

    # ==========================================
    # Statistics
    # ==========================================

    def get_statistics(self):

        self.cursor.execute("SELECT COUNT(*) FROM ALERT")
        total = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM ALERT WHERE STATUS='OPEN'")
        open_alert = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM ALERT WHERE STATUS='CLOSED'")
        closed = self.cursor.fetchone()[0]

        return {
            "total": total,
            "open": open_alert,
            "closed": closed
        }

    # ==========================================
    # Close
    # ==========================================

    def close(self):

        self.rule_engine.close()
        self.conn.close()


# =====================================
# Test
# =====================================
if __name__ == "__main__":
    import pandas as pd
    from pprint import pprint

    engine = AlertEngine()

    print("⏳ Đang quét Database để tạo cảnh báo cho giao dịch...")

    try:
        # Lấy danh sách toàn bộ mã giao dịch
        query = "SELECT TXN_ID FROM [TRANSACTION]"
        df_txns = pd.read_sql(query, engine.conn)
        
        found_alert = False
        
        for txn_id in df_txns["TXN_ID"]:
            result = engine.generate_alert(txn_id)
            
            # Chỉ in ra nếu đó là Alert mới được tạo
            if result.get("status") and result.get("message") != "Alert already exists.":
                print(f"\n🚨 Đã xử lý giao dịch: {txn_id} | Lifecycle: {result.get('alert_status')} | Action: {result.get('decision')}")
                pprint(result)
                found_alert = True
                break  # Dừng ở giao dịch đầu tiên được tạo alert thành công
                
        if not found_alert:
            print("\n✅ Không có cảnh báo mới nào được tạo.")
            
    except Exception as e:
        print(f"\n❌ Lỗi khi quét giao dịch: {e}")

    print("\n" + "="*40)
    print(" DANH SÁCH 5 CẢNH BÁO MỚI NHẤT")
    print("="*40)
    alerts = engine.get_alerts()
    if alerts:
        alerts_df = pd.DataFrame(alerts)
        print(alerts_df.head())
    else:
        print("Chưa có cảnh báo nào trong hệ thống.")

    print("\n" + "="*40)
    print(" THỐNG KÊ VÒNG ĐỜI CẢNH BÁO (STATUS)")
    print("="*40)
    pprint(engine.get_statistics())

    engine.close()