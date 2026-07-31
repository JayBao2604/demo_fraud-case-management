"""
FR001 - Card Fraud - Fraud Suspicious Account

Khởi tạo cảnh báo nếu giao dịch thực hiện từ thẻ nằm trong
danh sách tài khoản thanh toán / ví điện tử nghi ngờ gian lận,
giả mạo, vi phạm pháp luật.
"""

from modules.loader import DatabaseLoader


class FR001:

    RULE_ID = "FR001"
    RULE_NAME = "Card Fraud - Fraud Suspicious Account"

    # Danh sách thẻ / tài khoản nghi ngờ (demo blacklist)
    # Thực tế sẽ lấy từ hệ thống blacklist / watchlist của ngân hàng
    SUSPICIOUS_CARDS = {
        "CARD00010", "CARD00025", "CARD00050", "CARD00100",
        "CARD00200", "CARD00500", "CARD01000", "CARD02000",
        "CARD03000", "CARD04000", "CARD05000", "CARD06000",
        "CARD06651", "CARD07611", "CARD08000", "CARD09000",
    }

    # Khách hàng HIGH risk cũng được coi là nghi ngờ
    HIGH_RISK_RATINGS = {"HIGH"}

    def __init__(self):
        self.db = DatabaseLoader()

    def evaluate(self, transaction):
        """
        transaction: dict hoặc Series có CARD_ID, CUSTOMER_ID
        """
        card_id = str(transaction.get("CARD_ID", "")).strip()
        customer_id = str(transaction.get("CUSTOMER_ID", "")).strip()

        # 1. Kiểm tra blacklist thẻ
        if card_id in self.SUSPICIOUS_CARDS:
            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": True,
                "score": 50,
                "message": f"Thẻ {card_id} nằm trong danh sách tài khoản/ví nghi ngờ gian lận."
            }

        # 2. Kiểm tra khách hàng HIGH risk
        try:
            customer = self.db.get_customer(customer_id)
            if not customer.empty:
                risk = str(customer.iloc[0].get("RISK_RATING", "")).upper()
                if risk in self.HIGH_RISK_RATINGS:
                    return {
                        "rule_id": self.RULE_ID,
                        "rule_name": self.RULE_NAME,
                        "triggered": True,
                        "score": 40,
                        "message": f"Khách hàng {customer_id} thuộc nhóm rủi ro cao (HIGH)."
                    }
        except Exception:
            pass

        # 3. Kiểm tra thẻ bị BLOCKED
        try:
            card = self.db.query(
                "SELECT CARD_STATUS FROM CARD WHERE CARD_ID = ?",
                (card_id,)
            )
            if not card.empty and str(card.iloc[0]["CARD_STATUS"]).upper() == "BLOCKED":
                return {
                    "rule_id": self.RULE_ID,
                    "rule_name": self.RULE_NAME,
                    "triggered": True,
                    "score": 45,
                    "message": f"Thẻ {card_id} đang ở trạng thái BLOCKED."
                }
        except Exception:
            pass

        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": False,
            "score": 0,
            "message": "Thẻ/tài khoản không nằm trong danh sách nghi ngờ."
        }


if __name__ == "__main__":
    sample = {
        "CARD_ID": "CARD06651",
        "CUSTOMER_ID": "C06651"
    }
    rule = FR001()
    print(rule.evaluate(sample))
