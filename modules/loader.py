import sqlite3
from pathlib import Path
import pandas as pd

# ==========================================================
# Database Path
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "banking.db"


class DatabaseLoader:

    # ======================================================
    # INIT
    # ======================================================

    def __init__(self):
        pass

    # ======================================================
    # CONNECTION
    # ======================================================

    def get_connection(self):

        conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )

        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")

        return conn

    # ======================================================
    # HELPER
    # ======================================================

    def _normalize_id(self, value, column=None):

        if isinstance(value, pd.Series):

            if column and column in value.index:
                return value[column]

            return value.iloc[0]

        if isinstance(value, pd.DataFrame):

            if value.empty:
                return None

            if column and column in value.columns:
                return value.iloc[0][column]

            return value.iloc[0, 0]

        return value

    # ======================================================
    # QUERY
    # ======================================================

    def query(self, sql, params=()):

        conn = self.get_connection()

        try:

            return pd.read_sql_query(
                sql,
                conn,
                params=params
            )

        finally:

            conn.close()

    # ======================================================
    # EXECUTE
    # ======================================================

    def execute(self, sql, params=()):

        conn = self.get_connection()

        try:

            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()

            return cur.lastrowid

        finally:

            conn.close()

    # ======================================================
    # LOAD TABLE
    # ======================================================

    def load_customer(self):
        return self.query("SELECT * FROM CUSTOMER")

    def load_account(self):
        return self.query("SELECT * FROM ACCOUNT")

    def load_card(self):
        return self.query("SELECT * FROM CARD")

    def load_merchant(self):
        return self.query("SELECT * FROM MERCHANT")

    def load_terminal(self):
        return self.query("SELECT * FROM TERMINAL")

    def load_transaction(self):
        return self.query("SELECT * FROM TRANSACTION_HISTORY")

    def load_alert(self):
        return self.query("SELECT * FROM ALERT")

    def load_case(self):
        return self.query("SELECT * FROM FRAUD_CASE")

    # ======================================================
    # GET SINGLE RECORD
    # ======================================================

    def get_customer(self, customer_id):

        customer_id = self._normalize_id(customer_id, "CUSTOMER_ID")

        return self.query(
            """
            SELECT *
            FROM CUSTOMER
            WHERE CUSTOMER_ID=?
            """,
            (customer_id,)
        )

    def get_account(self, account_id):

        account_id = self._normalize_id(account_id, "ACCOUNT_ID")

        return self.query(
            """
            SELECT *
            FROM ACCOUNT
            WHERE ACCOUNT_ID=?
            """,
            (account_id,)
        )

    def get_card(self, card_id):

        card_id = self._normalize_id(card_id, "CARD_ID")

        return self.query(
            """
            SELECT *
            FROM CARD
            WHERE CARD_ID=?
            """,
            (card_id,)
        )

    def get_merchant(self, merchant_id):

        merchant_id = self._normalize_id(merchant_id, "MERCHANT_ID")

        return self.query(
            """
            SELECT *
            FROM MERCHANT
            WHERE MERCHANT_ID=?
            """,
            (merchant_id,)
        )

    def get_terminal(self, terminal_id):

        terminal_id = self._normalize_id(terminal_id, "TERMINAL_ID")

        return self.query(
            """
            SELECT *
            FROM TERMINAL
            WHERE TERMINAL_ID=?
            """,
            (terminal_id,)
        )

    def get_alert(self, alert_id):

        alert_id = self._normalize_id(alert_id, "ALERT_ID")

        return self.query(
            """
            SELECT *
            FROM ALERT
            WHERE ALERT_ID=?
            """,
            (alert_id,)
        )

    def get_case(self, case_id):

        case_id = self._normalize_id(case_id, "CASE_ID")

        return self.query(
            """
            SELECT *
            FROM FRAUD_CASE
            WHERE CASE_ID=?
            """,
            (case_id,)
        )
        # ======================================================
    # TRANSACTION
    # ======================================================

    def get_transaction(self, txn_id):

        txn_id = self._normalize_id(txn_id, "TXN_ID")

        return self.query(
            """
            SELECT

                T.*,

                C.FULL_NAME,
                C.RISK_RATING,
                C.AML_SCORE,
                C.KYC_LEVEL,

                CA.CARD_BRAND,
                CA.CARD_TYPE,
                CA.CARD_STATUS,

                M.MERCHANT_NAME,
                M.CATEGORY,
                M.RISK_LEVEL,

                TE.TERMINAL_TYPE,
                TE.CITY,

                A.ALERT_ID,
                A.ALERT_LEVEL,
                A.RULE_SCORE,
                A.STATUS AS ALERT_STATUS,

                F.CASE_ID,
                F.RISK_SCORE,
                F.STATUS AS CASE_STATUS

            FROM TRANSACTION_HISTORY T

            LEFT JOIN CUSTOMER C
                ON T.CUSTOMER_ID=C.CUSTOMER_ID

            LEFT JOIN CARD CA
                ON T.CARD_ID=CA.CARD_ID

            LEFT JOIN MERCHANT M
                ON T.MERCHANT_ID=M.MERCHANT_ID

            LEFT JOIN TERMINAL TE
                ON T.TERMINAL_ID=TE.TERMINAL_ID

            LEFT JOIN ALERT A
                ON T.TXN_ID=A.TXN_ID

            LEFT JOIN FRAUD_CASE F
                ON T.TXN_ID=F.TXN_ID

            WHERE T.TXN_ID=?
            """,
            (txn_id,)
        )

    # ======================================================
    # SEARCH
    # ======================================================

    def get_transactions_by_customer(self, customer_id):

        customer_id = self._normalize_id(customer_id, "CUSTOMER_ID")

        return self.query(
            """
            SELECT

                T.TXN_ID,
                T.TXN_TIME,
                T.AMOUNT,
                T.COUNTRY,

                CA.CARD_BRAND,
                CA.CARD_TYPE,

                M.MERCHANT_NAME,

                TE.CITY,

                IFNULL(A.ALERT_LEVEL,'-') AS ALERT_LEVEL,
                IFNULL(A.STATUS,'-') AS ALERT_STATUS,

                IFNULL(F.CASE_ID,'-') AS CASE_ID,
                IFNULL(F.STATUS,'-') AS CASE_STATUS,
                IFNULL(F.RISK_SCORE,'-') AS CASE_RISK_SCORE

            FROM TRANSACTION_HISTORY T

            LEFT JOIN CARD CA
                ON T.CARD_ID=CA.CARD_ID

            LEFT JOIN MERCHANT M
                ON T.MERCHANT_ID=M.MERCHANT_ID

            LEFT JOIN TERMINAL TE
                ON T.TERMINAL_ID=TE.TERMINAL_ID

            LEFT JOIN ALERT A
                ON T.TXN_ID=A.TXN_ID

            LEFT JOIN FRAUD_CASE F
                ON T.TXN_ID=F.TXN_ID

            WHERE T.CUSTOMER_ID=?

            ORDER BY T.TXN_TIME DESC
            """,
            (customer_id,)
        )

    def get_transactions_by_card(self, card_id):

        card_id = self._normalize_id(card_id, "CARD_ID")

        return self.query(
            """
            SELECT

                T.TXN_ID,
                T.TXN_TIME,
                T.AMOUNT,
                T.COUNTRY,

                C.FULL_NAME,

                M.MERCHANT_NAME,

                TE.CITY,

                IFNULL(A.ALERT_LEVEL,'-') AS ALERT_LEVEL,
                IFNULL(A.STATUS,'-') AS ALERT_STATUS,

                IFNULL(F.CASE_ID,'-') AS CASE_ID,
                IFNULL(F.STATUS,'-') AS CASE_STATUS,
                IFNULL(F.RISK_SCORE,'-') AS CASE_RISK_SCORE

            FROM TRANSACTION_HISTORY T

            LEFT JOIN CUSTOMER C
                ON T.CUSTOMER_ID=C.CUSTOMER_ID

            LEFT JOIN MERCHANT M
                ON T.MERCHANT_ID=M.MERCHANT_ID

            LEFT JOIN TERMINAL TE
                ON T.TERMINAL_ID=TE.TERMINAL_ID

            LEFT JOIN ALERT A
                ON T.TXN_ID=A.TXN_ID

            LEFT JOIN FRAUD_CASE F
                ON T.TXN_ID=F.TXN_ID

            WHERE T.CARD_ID=?

            ORDER BY T.TXN_TIME DESC
            """,
            (card_id,)
        )

    def get_transactions_by_merchant(self, merchant_id):

        merchant_id = self._normalize_id(merchant_id, "MERCHANT_ID")

        return self.query(
            """
            SELECT

                T.TXN_ID,
                T.TXN_TIME,
                T.AMOUNT,
                T.COUNTRY,

                C.FULL_NAME,

                CA.CARD_BRAND,

                TE.CITY,

                IFNULL(A.STATUS,'-') AS ALERT_STATUS,
                IFNULL(F.STATUS,'-') AS CASE_STATUS

            FROM TRANSACTION_HISTORY T

            LEFT JOIN CUSTOMER C
                ON T.CUSTOMER_ID=C.CUSTOMER_ID

            LEFT JOIN CARD CA
                ON T.CARD_ID=CA.CARD_ID

            LEFT JOIN TERMINAL TE
                ON T.TERMINAL_ID=TE.TERMINAL_ID

            LEFT JOIN ALERT A
                ON T.TXN_ID=A.TXN_ID

            LEFT JOIN FRAUD_CASE F
                ON T.TXN_ID=F.TXN_ID

            WHERE T.MERCHANT_ID=?

            ORDER BY T.TXN_TIME DESC
            """,
            (merchant_id,)
        )

    def get_transactions_by_country(self, country):

        return self.query(
            """
            SELECT

                T.TXN_ID,
                T.TXN_TIME,
                T.AMOUNT,

                C.FULL_NAME,

                CA.CARD_BRAND,

                M.MERCHANT_NAME,

                TE.CITY,

                IFNULL(A.STATUS,'-') AS ALERT_STATUS,
                IFNULL(F.STATUS,'-') AS CASE_STATUS

            FROM TRANSACTION_HISTORY T

            LEFT JOIN CUSTOMER C
                ON T.CUSTOMER_ID=C.CUSTOMER_ID

            LEFT JOIN CARD CA
                ON T.CARD_ID=CA.CARD_ID

            LEFT JOIN MERCHANT M
                ON T.MERCHANT_ID=M.MERCHANT_ID

            LEFT JOIN TERMINAL TE
                ON T.TERMINAL_ID=TE.TERMINAL_ID

            LEFT JOIN ALERT A
                ON T.TXN_ID=A.TXN_ID

            LEFT JOIN FRAUD_CASE F
                ON T.TXN_ID=F.TXN_ID

            WHERE T.COUNTRY=?

            ORDER BY T.TXN_TIME DESC
            """,
            (country,)
        )
        # ======================================================
    # ALERT
    # ======================================================

    def create_alert(
        self,
        txn_id,
        customer_id,
        level,
        score,
        status="OPEN"
    ):

        return self.execute(
            """
            INSERT INTO ALERT
            (
                TXN_ID,
                CUSTOMER_ID,
                ALERT_LEVEL,
                RULE_SCORE,
                STATUS,
                CREATED_TIME
            )
            VALUES
            (
                ?, ?, ?, ?, ?,
                datetime('now')
            )
            """,
            (
                txn_id,
                customer_id,
                level,
                score,
                status
            )
        )

    def update_alert_status(self, alert_id, status):

        self.execute(
            """
            UPDATE ALERT
            SET STATUS=?
            WHERE ALERT_ID=?
            """,
            (
                status,
                alert_id
            )
        )

    # ======================================================
    # FRAUD CASE
    # ======================================================

    def create_case(
        self,
        case_id,
        txn_id,
        risk_score,
        status="OPEN"
    ):

        self.execute(
            """
            INSERT INTO FRAUD_CASE
            (
                CASE_ID,
                TXN_ID,
                RISK_SCORE,
                STATUS,
                CREATED_TIME
            )
            VALUES
            (
                ?, ?, ?, ?,
                datetime('now')
            )
            """,
            (
                case_id,
                txn_id,
                risk_score,
                status
            )
        )

    def update_case_status(
        self,
        case_id,
        status
    ):

        self.execute(
            """
            UPDATE FRAUD_CASE
            SET STATUS=?
            WHERE CASE_ID=?
            """,
            (
                status,
                case_id
            )
        )

    # ======================================================
    # DASHBOARD
    # ======================================================

    def get_dashboard_summary(self):

        return {

            "customer":
            self.query(
                "SELECT COUNT(*) TOTAL FROM CUSTOMER"
            ).iloc[0]["TOTAL"],

            "account":
            self.query(
                "SELECT COUNT(*) TOTAL FROM ACCOUNT"
            ).iloc[0]["TOTAL"],

            "card":
            self.query(
                "SELECT COUNT(*) TOTAL FROM CARD"
            ).iloc[0]["TOTAL"],

            "merchant":
            self.query(
                "SELECT COUNT(*) TOTAL FROM MERCHANT"
            ).iloc[0]["TOTAL"],

            "terminal":
            self.query(
                "SELECT COUNT(*) TOTAL FROM TERMINAL"
            ).iloc[0]["TOTAL"],

            "transaction":
            self.query(
                "SELECT COUNT(*) TOTAL FROM TRANSACTION_HISTORY"
            ).iloc[0]["TOTAL"],

            "alert":
            self.query(
                "SELECT COUNT(*) TOTAL FROM ALERT"
            ).iloc[0]["TOTAL"],

            "case":
            self.query(
                "SELECT COUNT(*) TOTAL FROM FRAUD_CASE"
            ).iloc[0]["TOTAL"]

        }

    # ======================================================
    # TRANSACTION DETAIL
    # ======================================================

    def transaction_detail(self):

        return self.query(
            """
            SELECT

                T.*,

                C.FULL_NAME,
                C.RISK_RATING,

                CA.CARD_BRAND,
                CA.CARD_TYPE,

                M.MERCHANT_NAME,
                M.CATEGORY,
                M.RISK_LEVEL,

                TE.CITY,
                TE.TERMINAL_TYPE,

                A.ALERT_LEVEL,
                A.STATUS AS ALERT_STATUS,

                F.CASE_ID,
                F.STATUS AS CASE_STATUS

            FROM TRANSACTION_HISTORY T

            LEFT JOIN CUSTOMER C
                ON T.CUSTOMER_ID=C.CUSTOMER_ID

            LEFT JOIN CARD CA
                ON T.CARD_ID=CA.CARD_ID

            LEFT JOIN MERCHANT M
                ON T.MERCHANT_ID=M.MERCHANT_ID

            LEFT JOIN TERMINAL TE
                ON T.TERMINAL_ID=TE.TERMINAL_ID

            LEFT JOIN ALERT A
                ON T.TXN_ID=A.TXN_ID

            LEFT JOIN FRAUD_CASE F
                ON T.TXN_ID=F.TXN_ID

            ORDER BY T.TXN_TIME DESC
            """
        )

    # ======================================================
    # CLOSE
    # ======================================================

    def close(self):
        pass