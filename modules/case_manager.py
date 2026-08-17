"""
modules/case_manager.py
------------------------------------
Fraud Case Management
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd

from modules.alert_engine import AlertEngine

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "banking.db"


class CaseManager:

    def __init__(self):

        self.alert_engine = AlertEngine()

        # Giữ tham số check_same_thread=False để tương thích với Streamlit
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

        self.create_case_table()

    # =====================================
    # Create Table
    # =====================================

    def create_case_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS FRAUD_CASE(
            CASE_ID TEXT PRIMARY KEY,
            TXN_ID TEXT,
            RISK_SCORE INTEGER,
            STATUS TEXT,
            CREATED_TIME TEXT,
            FOREIGN KEY(TXN_ID) REFERENCES [TRANSACTION](TXN_ID)
        )
        """)

        self.conn.commit()

    # =====================================
    # Update Severity (Risk Score)
    # =====================================

    def update_severity(self, case_id, risk_score):
        self.cursor.execute("""
            UPDATE FRAUD_CASE
            SET RISK_SCORE=?
            WHERE CASE_ID=?
        """, (risk_score, case_id))
        self.conn.commit()

    # =====================================
    # Check Existing Case
    # =====================================

    def case_exists(self, txn_id):

        self.cursor.execute("""
            SELECT CASE_ID
            FROM FRAUD_CASE
            WHERE TXN_ID=?
        """, (txn_id,))

        return self.cursor.fetchone() is not None

    # =====================================
    # Create Case (Linked to Alert)
    # =====================================

    def create_case(self, txn_id, risk_score=0):

        if self.case_exists(txn_id):
            return {
                "status": False,
                "message": "Case already exists for this transaction."
            }

        # Sinh Alert trước khi tạo Case
        alert_result = self.alert_engine.generate_alert(txn_id)

        if not alert_result.get("status"):
            return {
                "status": False,
                "message": alert_result.get("message", "No alert generated, skipping case creation.")
            }

        # Lấy điểm rủi ro từ Alert (nếu có), nếu không dùng mặc định
        alert_data = alert_result.get("alert", {})
        final_risk_score = alert_data.get("rule_score", risk_score)
        
        # Tạo CASE_ID đồng bộ với TXN_ID
        case_id = f"CASE-{txn_id}"
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute("""
        INSERT INTO FRAUD_CASE(
            CASE_ID,
            TXN_ID,
            RISK_SCORE,
            STATUS,
            CREATED_TIME
        )
        VALUES(?, ?, ?, ?, ?)
        """, (case_id, txn_id, final_risk_score, "OPEN", created_time))

        self.conn.commit()

        return {
            "status": True,
            "message": f"Fraud case {case_id} created successfully.",
            "case": {
                "CASE_ID": case_id,
                "TXN_ID": txn_id,
                "RISK_SCORE": final_risk_score,
                "STATUS": "OPEN",
                "CREATED_TIME": created_time
            }
        }

    # =====================================
    # Update Status
    # =====================================

    def update_status(self, case_id, status):

        self.cursor.execute("""
            UPDATE FRAUD_CASE
            SET STATUS=?
            WHERE CASE_ID=?
        """, (status, case_id))

        self.conn.commit()

    # =====================================
    # Close Case
    # =====================================

    def close_case(self, case_id):

        self.update_status(case_id, "CLOSED")

    # =====================================
    # Get One Case (By TXN_ID to support Live Transaction view)
    # =====================================

    def get_case(self, txn_id):

        self.cursor.execute("""
            SELECT *
            FROM FRAUD_CASE
            WHERE TXN_ID=?
        """, (txn_id,))

        row = self.cursor.fetchone()

        if row:
            return {
                "status": True,
                "case": dict(row)
            }

        return {
            "status": False,
            "message": "No case found for this transaction."
        }

    # =====================================
    # Get Cases (For Case Manager Dataframe)
    # =====================================

    def get_cases(self):

        query = """
        SELECT *
        FROM FRAUD_CASE
        ORDER BY CREATED_TIME DESC
        """

        return pd.read_sql_query(query, self.conn)

    # =====================================
    # Open Cases
    # =====================================

    def open_cases(self):

        query = """
        SELECT *
        FROM FRAUD_CASE
        WHERE STATUS='OPEN'
        ORDER BY CREATED_TIME DESC
        """

        return pd.read_sql_query(query, self.conn)

    # =====================================
    # Delete Case
    # =====================================

    def delete_case(self, case_id):

        self.cursor.execute("""
            DELETE
            FROM FRAUD_CASE
            WHERE CASE_ID=?
        """, (case_id,))

        self.conn.commit()

    # =====================================
    # Statistics
    # =====================================

    def statistics(self):

        self.cursor.execute("SELECT COUNT(*) FROM FRAUD_CASE")
        total = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM FRAUD_CASE WHERE STATUS='OPEN'")
        open_case = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM FRAUD_CASE WHERE STATUS='CLOSED'")
        closed = self.cursor.fetchone()[0]

        return {
            "total": total,
            "open": open_case,
            "closed": closed
        }

    # =====================================
    # Close Connection
    # =====================================

    def close(self):

        self.alert_engine.close()
        self.conn.close()


if __name__ == "__main__":

    manager = CaseManager()
    
    # Test thử tạo case
    print(manager.create_case("TXN005"))
    print()
    
    # In thống kê
    print(manager.statistics())
    print()
    
    # Xem dữ liệu cases
    print(manager.get_cases())
    
    manager.close()