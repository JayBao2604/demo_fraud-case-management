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

        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

        self.create_case_table()

    # =====================================
    # Create Table
    # =====================================

    def create_case_table(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS FRAUD_CASE(

            CASE_ID INTEGER PRIMARY KEY AUTOINCREMENT,

            ALERT_ID INTEGER,

            TXN_ID TEXT,

            CUSTOMER_ID TEXT,

            PRIORITY TEXT,

            ASSIGNED_TO TEXT,

            STATUS TEXT,

            CREATED_TIME TEXT,

            CLOSED_TIME TEXT,

            REMARK TEXT

        )

        """)

        self.conn.commit()

    # =====================================
    # Priority
    # =====================================

    def priority(self, level):

        mapping = {
            "CRITICAL": "P1",
            "HIGH": "P2",
            "MEDIUM": "P3",
            "LOW": "P4"
        }

        return mapping.get(level, "P4")

    # =====================================
    # Check Existing Case
    # =====================================

    def case_exists(self, txn_id):

        self.cursor.execute("""

            SELECT CASE_ID

            FROM FRAUD_CASE

            WHERE TXN_ID=?

            AND STATUS='OPEN'

        """, (txn_id,))

        return self.cursor.fetchone() is not None

    # =====================================
    # Create Case
    # =====================================

    def create_case(self, txn_id):

        if self.case_exists(txn_id):

            return {

                "status": False,

                "message": "Case already exists."

            }

        alert = self.alert_engine.generate_alert(txn_id)

        if not alert["status"]:
            return alert

        if "alert_level" not in alert:

            return {

                "status": False,

                "message": "No alert generated."

            }

        self.cursor.execute("""

            SELECT ALERT_ID

            FROM ALERT

            WHERE TXN_ID=?

            ORDER BY ALERT_ID DESC

            LIMIT 1

        """, (txn_id,))

        row = self.cursor.fetchone()

        if row is None:

            return {

                "status": False,

                "message": "Alert not found."

            }

        alert_id = row["ALERT_ID"]

        priority = self.priority(alert["alert_level"])

        self.cursor.execute("""

        INSERT INTO FRAUD_CASE(

            ALERT_ID,

            TXN_ID,

            CUSTOMER_ID,

            PRIORITY,

            ASSIGNED_TO,

            STATUS,

            CREATED_TIME,

            CLOSED_TIME,

            REMARK

        )

        VALUES(?,?,?,?,?,?,?,?,?)

        """, (

            alert_id,

            alert["transaction_id"],

            alert["customer_id"],

            priority,

            "",

            "OPEN",

            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "",

            ""

        ))

        self.conn.commit()

        return {

            "status": True,

            "case_id": self.cursor.lastrowid,

            "alert_id": alert_id,

            "priority": priority,

            "transaction_id": alert["transaction_id"],

            "customer_id": alert["customer_id"]

        }

    # =====================================
    # Assign Case
    # =====================================

    def assign_case(self, case_id, analyst):

        self.cursor.execute("""

            UPDATE FRAUD_CASE

            SET ASSIGNED_TO=?

            WHERE CASE_ID=?

        """, (analyst, case_id))

        self.conn.commit()

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

    def close_case(self, case_id, remark=""):

        self.cursor.execute("""

            UPDATE FRAUD_CASE

            SET

                STATUS='CLOSED',

                CLOSED_TIME=?,

                REMARK=?

            WHERE CASE_ID=?

        """, (

            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            remark,

            case_id

        ))

        self.conn.commit()

    # =====================================
    # Get One Case
    # =====================================

    def get_case(self, case_id):

        self.cursor.execute("""

            SELECT *

            FROM FRAUD_CASE

            WHERE CASE_ID=?

        """, (case_id,))

        row = self.cursor.fetchone()

        if row:

            return dict(row)

        return None

    # =====================================
    # Get Cases
    # =====================================

    def get_cases(self):

        query = """

        SELECT *

        FROM FRAUD_CASE

        ORDER BY CASE_ID DESC

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

        ORDER BY CASE_ID DESC

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

        self.cursor.execute("""

            SELECT COUNT(*)

            FROM FRAUD_CASE

        """)

        total = self.cursor.fetchone()[0]

        self.cursor.execute("""

            SELECT COUNT(*)

            FROM FRAUD_CASE

            WHERE STATUS='OPEN'

        """)

        open_case = self.cursor.fetchone()[0]

        self.cursor.execute("""

            SELECT COUNT(*)

            FROM FRAUD_CASE

            WHERE STATUS='CLOSED'

        """)

        closed = self.cursor.fetchone()[0]

        return {

            "total": total,

            "open": open_case,

            "closed": closed

        }

    # =====================================
    # Close
    # =====================================

    def close(self):

        self.alert_engine.close()

        self.conn.close()


if __name__ == "__main__":

    manager = CaseManager()

    print(manager.create_case("TXN005"))

    print()

    print(manager.statistics())

    print()

    print(manager.get_cases())

    manager.close()