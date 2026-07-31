"""
FR025 - Card Fraud - Unusual Transaction Alert

Khởi tạo cảnh báo nếu thẻ thực hiện [n1] giao dịch trong vòng [n2] giờ,
với giá trị giao dịch lớn hơn [m] VND, trong các khung giờ [h1 - h2]
mà trong [n3] tháng/quý/năm người dùng thẻ chưa bao giờ phát sinh giao dịch.
"""

from datetime import datetime, timedelta
import pandas as pd
from modules.loader import DatabaseLoader


class FR025:

    RULE_ID = "FR025"
    RULE_NAME = "Card Fraud - Unusual Transaction Alert"

    # Tham số cấu hình
    N1_TXN_COUNT = 3              # [n1] số giao dịch
    N2_HOURS = 2                  # [n2] giờ
    AMOUNT_THRESHOLD = 3_000_000  # [m] VND
    NIGHT_START = 23              # [h1] bắt đầu khung giờ bất thường
    NIGHT_END = 6                 # [h2] kết thúc khung giờ bất thường
    LOOKBACK_MONTHS = 6           # [n3] tháng lịch sử

    def __init__(self):
        self.db = DatabaseLoader()

    def _is_unusual_hour(self, hour: int) -> bool:
        """Kiểm tra giờ có thuộc khung bất thường (ban đêm) không."""
        if self.NIGHT_START > self.NIGHT_END:
            # Ví dụ 23h -> 6h
            return hour >= self.NIGHT_START or hour < self.NIGHT_END
        return self.NIGHT_START <= hour < self.NIGHT_END

    def evaluate(self, transaction):
        """
        transaction: dict/Series có CARD_ID, AMOUNT, TXN_TIME
        """
        card_id = str(transaction.get("CARD_ID", "")).strip()
        amount = float(transaction.get("AMOUNT", 0) or 0)

        try:
            txn_time = pd.to_datetime(transaction.get("TXN_TIME"))
        except Exception:
            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": False,
                "score": 0,
                "message": "Không đọc được thời gian giao dịch."
            }

        current_hour = txn_time.hour

        # 1. Giao dịch hiện tại phải nằm trong khung giờ bất thường
        if not self._is_unusual_hour(current_hour):
            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": False,
                "score": 0,
                "message": (
                    f"Giao dịch lúc {current_hour}h không thuộc khung giờ bất thường "
                    f"({self.NIGHT_START}h-{self.NIGHT_END}h)."
                )
            }

        # 2. Giá trị giao dịch phải > ngưỡng
        if amount < self.AMOUNT_THRESHOLD:
            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": False,
                "score": 0,
                "message": (
                    f"Giá trị {amount:,.0f} VND chưa vượt ngưỡng "
                    f"{self.AMOUNT_THRESHOLD:,.0f} VND."
                )
            }

        # 3. Đếm số giao dịch của thẻ trong cửa sổ [n2] giờ gần nhất
        window_start = txn_time - timedelta(hours=self.N2_HOURS)

        try:
            recent = self.db.query(
                """
                SELECT TXN_ID, AMOUNT, TXN_TIME
                FROM [TRANSACTION]
                WHERE CARD_ID = ?
                  AND TXN_TIME >= ?
                  AND TXN_TIME <= ?
                """,
                (card_id, str(window_start), str(txn_time))
            )
        except Exception:
            recent = pd.DataFrame()

        recent_count = len(recent) if not recent.empty else 1

        if recent_count < self.N1_TXN_COUNT:
            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": False,
                "score": 0,
                "message": (
                    f"Chỉ có {recent_count} giao dịch trong {self.N2_HOURS} giờ "
                    f"(yêu cầu >= {self.N1_TXN_COUNT})."
                )
            }

        # 4. Kiểm tra lịch sử: trong [n3] tháng trước, thẻ đã từng giao dịch ở khung giờ này chưa?
        history_start = txn_time - timedelta(days=30 * self.LOOKBACK_MONTHS)

        try:
            history = self.db.query(
                """
                SELECT TXN_TIME
                FROM [TRANSACTION]
                WHERE CARD_ID = ?
                  AND TXN_TIME < ?
                  AND TXN_TIME >= ?
                """,
                (card_id, str(window_start), str(history_start))
            )
        except Exception:
            history = pd.DataFrame()

        has_history_in_unusual_hour = False
        if not history.empty:
            for t in pd.to_datetime(history["TXN_TIME"]):
                if self._is_unusual_hour(t.hour):
                    has_history_in_unusual_hour = True
                    break

        if has_history_in_unusual_hour:
            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": False,
                "score": 0,
                "message": (
                    f"Thẻ đã từng giao dịch trong khung giờ {self.NIGHT_START}h-{self.NIGHT_END}h "
                    f"trong {self.LOOKBACK_MONTHS} tháng gần đây."
                )
            }

        # Tất cả điều kiện thỏa → Trigger
        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": True,
            "score": 40,
            "message": (
                f"Thẻ thực hiện {recent_count} giao dịch trong {self.N2_HOURS} giờ "
                f"(giá trị >= {self.AMOUNT_THRESHOLD:,.0f} VND) trong khung giờ bất thường "
                f"{self.NIGHT_START}h-{self.NIGHT_END}h, trong khi {self.LOOKBACK_MONTHS} tháng "
                f"gần đây chưa từng giao dịch ở khung giờ này."
            )
        }


if __name__ == "__main__":
    sample = {
        "CARD_ID": "CARD00001",
        "AMOUNT": 5_000_000,
        "TXN_TIME": "2026-07-28 02:30:00"
    }
    rule = FR025()
    print(rule.evaluate(sample))
