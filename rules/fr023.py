"""
FR023 - Card Fraud - Unusual Payment Channel

Khởi tạo cảnh báo nếu giao dịch thẻ thanh toán qua các kênh
mà trước đó thẻ chưa từng thanh toán (ví dụ Facebook, merchant mới...)
trong vòng [n] tháng gần nhất, với giá trị giao dịch vượt quá
[m] VND hoặc [p%] hạn mức thẻ.
"""

from datetime import datetime, timedelta
import pandas as pd
from modules.loader import DatabaseLoader


class FR023:

    RULE_ID = "FR023"
    RULE_NAME = "Card Fraud - Unusual Payment Channel"

    # Tham số cấu hình (có thể chỉnh trong Rule Manager)
    LOOKBACK_MONTHS = 3          # [n] tháng gần nhất
    AMOUNT_THRESHOLD = 5_000_000 # [m] VND
    LIMIT_PERCENT = 0.20         # [p%] hạn mức thẻ (20%)

    def __init__(self):
        self.db = DatabaseLoader()

    def evaluate(self, transaction):
        """
        transaction: dict/Series có CARD_ID, MERCHANT_ID, AMOUNT, TXN_TIME
        """
        card_id = str(transaction.get("CARD_ID", "")).strip()
        merchant_id = str(transaction.get("MERCHANT_ID", "")).strip()
        amount = float(transaction.get("AMOUNT", 0) or 0)

        # Lấy thời gian giao dịch hiện tại
        try:
            txn_time = pd.to_datetime(transaction.get("TXN_TIME"))
        except Exception:
            txn_time = datetime.now()

        lookback_start = txn_time - timedelta(days=30 * self.LOOKBACK_MONTHS)

        # 1. Lấy lịch sử giao dịch của thẻ trong lookback period (trừ giao dịch hiện tại)
        try:
            history = self.db.query(
                """
                SELECT MERCHANT_ID, AMOUNT, TXN_TIME
                FROM [TRANSACTION]
                WHERE CARD_ID = ?
                  AND TXN_TIME < ?
                  AND TXN_TIME >= ?
                """,
                (card_id, str(txn_time), str(lookback_start))
            )
        except Exception:
            history = pd.DataFrame()

        # 2. Kiểm tra đây có phải kênh (merchant) mới không
        known_merchants = set()
        if not history.empty and "MERCHANT_ID" in history.columns:
            known_merchants = set(history["MERCHANT_ID"].astype(str).unique())

        is_new_channel = merchant_id not in known_merchants

        if not is_new_channel:
            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": False,
                "score": 0,
                "message": f"Merchant {merchant_id} đã từng được sử dụng bởi thẻ này."
            }

        # 3. Lấy hạn mức thẻ
        credit_limit = 0
        try:
            card = self.db.query(
                "SELECT CREDIT_LIMIT FROM CARD WHERE CARD_ID = ?",
                (card_id,)
            )
            if not card.empty:
                credit_limit = float(card.iloc[0]["CREDIT_LIMIT"] or 0)
        except Exception:
            pass

        # 4. Điều kiện giá trị giao dịch
        exceed_amount = amount >= self.AMOUNT_THRESHOLD
        exceed_percent = False
        if credit_limit > 0:
            exceed_percent = amount >= (credit_limit * self.LIMIT_PERCENT)

        if exceed_amount or exceed_percent:
            reason_parts = []
            if exceed_amount:
                reason_parts.append(
                    f"số tiền {amount:,.0f} VND >= ngưỡng {self.AMOUNT_THRESHOLD:,.0f} VND"
                )
            if exceed_percent:
                reason_parts.append(
                    f"số tiền đạt {amount/credit_limit*100:.1f}% hạn mức thẻ ({credit_limit:,.0f})"
                )

            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": True,
                "score": 45,
                "message": (
                    f"Thẻ thanh toán qua kênh mới ({merchant_id}) trong {self.LOOKBACK_MONTHS} tháng gần nhất. "
                    + "; ".join(reason_parts)
                )
            }

        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": False,
            "score": 0,
            "message": (
                f"Kênh mới nhưng giá trị {amount:,.0f} VND chưa vượt ngưỡng "
                f"({self.AMOUNT_THRESHOLD:,.0f} VND / {self.LIMIT_PERCENT*100:.0f}% hạn mức)."
            )
        }


if __name__ == "__main__":
    sample = {
        "CARD_ID": "CARD00001",
        "MERCHANT_ID": "M025",
        "AMOUNT": 15_000_000,
        "TXN_TIME": "2026-07-28 14:00:00"
    }
    rule = FR023()
    print(rule.evaluate(sample))
