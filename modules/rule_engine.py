"""
modules/rule_engine.py
------------------------------------


"""

import pandas as pd
from modules.loader import DatabaseLoader

from rules.fr001 import FR001
from rules.fr023 import FR023
from rules.fr025 import FR025


class RuleEngine:
    """
    Rule Engine for evaluating fraud risk on transactions.
    """

    BLOCK_THRESHOLD = 80
    REVIEW_THRESHOLD = 40

    def __init__(self):
        self.db = DatabaseLoader()
        self.fr001 = FR001()
        self.fr023 = FR023()
        self.fr025 = FR025()

    # =====================================
    # Evaluate Rules
    # =====================================
    def evaluate(self, txn_id):
        """
        Evaluate all fraud rules for one transaction.
        """
        txn = self.db.get_transaction(txn_id)

        if txn.empty:
            return {
                "status": False,
                "message": "Transaction not found"
            }

        txn = txn.iloc[0]
        # Convert to dict for rule compatibility
        txn_dict = txn.to_dict() if hasattr(txn, "to_dict") else dict(txn)

        score = 0
        triggered = []
        messages = []

        # ----- FR001: Suspicious Account -----
        r1 = self.fr001.evaluate(txn_dict)
        if r1.get("triggered"):
            triggered.append(r1["rule_id"])
            score += r1.get("score", 0)
            messages.append(r1.get("message", ""))

        # ----- FR023: Unusual Payment Channel -----
        r2 = self.fr023.evaluate(txn_dict)
        if r2.get("triggered"):
            triggered.append(r2["rule_id"])
            score += r2.get("score", 0)
            messages.append(r2.get("message", ""))

        # ----- FR025: Unusual Transaction Alert -----
        r3 = self.fr025.evaluate(txn_dict)
        if r3.get("triggered"):
            triggered.append(r3["rule_id"])
            score += r3.get("score", 0)
            messages.append(r3.get("message", ""))

        if score >= self.BLOCK_THRESHOLD:
            decision = "BLOCK"
        elif score >= self.REVIEW_THRESHOLD:
            decision = "REVIEW"
        else:
            decision = "PASS"

        rules_string = ", ".join(triggered) if triggered else "None"

        return {
            "status": True,
            "transaction_id": txn["TXN_ID"],
            "customer_id": txn["CUSTOMER_ID"],
            "rule_score": score,
            "triggered_rules": rules_string,
            "messages": messages,
            "decision": decision,
            "details": {
                "FR001": r1,
                "FR023": r2,
                "FR025": r3,
            }
        }

    # =====================================
    # Evaluate All
    # =====================================
    def evaluate_all(self, txn_id):
        """
        Evaluate transaction and return overall fraud assessment.
        """
        result = self.evaluate(txn_id)

        if not result.get("status"):
            return result

        score = result["rule_score"]

        if score >= self.BLOCK_THRESHOLD:
            risk = "HIGH"
        elif score >= self.REVIEW_THRESHOLD:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return {
            "status": True,
            "transaction_id": result["transaction_id"],
            "customer_id": result["customer_id"],
            "score": score,
            "risk": risk,
            "decision": result["decision"],
            "rules": result["triggered_rules"],
            "messages": result.get("messages", []),
            "details": result.get("details", {}),
        }

    # =====================================
    # Close
    # =====================================
    def close(self):
        """
        Close database connection.
        """
        self.db.close()


# =====================================
# Test
# =====================================
if __name__ == "__main__":
    from pprint import pprint

    engine = RuleEngine()

    print("Đang quét Database để tìm giao dịch vi phạm...")

    query = "SELECT TXN_ID FROM [TRANSACTION] LIMIT 200"
    df_txns = pd.read_sql(query, engine.db.get_connection())

    found = 0
    for txn_id in df_txns["TXN_ID"]:
        result = engine.evaluate_all(txn_id)
        if result.get("status") and result.get("risk") in ["HIGH", "MEDIUM"]:
            print(f"\nĐã tìm thấy giao dịch vi phạm: {txn_id}")
            pprint(result)
            found += 1
            if found >= 3:
                break

    if found == 0:
        print("\nKhông tìm thấy giao dịch nào vi phạm rủi ro trong mẫu dữ liệu.")

    engine.close()
