"""
modules/rule_engine.py
------------------------------------
Fraud Rule Engine
"""

from modules.loader import DatabaseLoader


class RuleEngine:
    """
    Rule Engine for evaluating fraud risk on transactions.
    """

    # -----------------------------
    # Threshold configuration
    # -----------------------------
    LARGE_AMOUNT_THRESHOLD = 10_000_000

    HIGH_RISK_COUNTRIES = [
        "IR",
        "KP",
        "SY",
        "AF",
        "RU"
    ]

    BLOCK_THRESHOLD = 80
    REVIEW_THRESHOLD = 40

    def __init__(self):
        self.db = DatabaseLoader()

    # =====================================
    # Rule 1: Large Amount
    # =====================================
    def large_amount(self, txn):
        """
        Trigger when transaction amount exceeds threshold.
        """

        if txn["AMOUNT"] >= self.LARGE_AMOUNT_THRESHOLD:
            return True, 30

        return False, 0

    # =====================================
    # Rule 2: High Risk Country
    # =====================================
    def high_risk_country(self, txn):
        """
        Trigger when transaction originates from
        a high-risk country.
        """

        if txn["COUNTRY"] in self.HIGH_RISK_COUNTRIES:
            return True, 25

        return False, 0

    # =====================================
    # Rule 3: New Device
    # =====================================
    def new_device(self, txn):
        """
        Trigger when customer uses a new device.
        """

        if txn["DEVICE_ID"] == "NEW_DEVICE":
            return True, 20

        return False, 0

    # =====================================
    # Rule 4: High Risk Merchant
    # =====================================
    def merchant_rule(self, txn):
        """
        Trigger when merchant is marked HIGH risk.
        """

        merchant = self.db.get_merchant(txn["MERCHANT_ID"])

        if merchant.empty:
            return False, 0

        merchant = merchant.iloc[0]

        if merchant["RISK_LEVEL"] == "HIGH":
            return True, 20

        return False, 0
        # =====================================
    # Rule 5: Night Transaction
    # =====================================
    def night_transaction(self, txn):
        """
        Trigger when transaction is performed
        during late night hours.
        """

        try:
            hour = int(str(txn["TXN_TIME"])[11:13])
        except Exception:
            return False, 0

        if hour < 6 or hour >= 23:
            return True, 15

        return False, 0

    # =====================================
    # Rule 6: Velocity
    # =====================================
    def velocity_rule(self, txn):
        """
        Trigger when customer has too many
        transactions.
        """

        df = self.db.load_transaction()

        customer = txn["CUSTOMER_ID"]

        count = len(
            df[df["CUSTOMER_ID"] == customer]
        )

        if count >= 5:
            return True, 25

        return False, 0

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

        score = 0
        triggered = []

        rules = [

            ("Large Amount", self.large_amount),

            ("High Risk Country", self.high_risk_country),

            ("New Device", self.new_device),

            ("High Risk Merchant", self.merchant_rule),

            ("Night Transaction", self.night_transaction),

            ("Velocity", self.velocity_rule)

        ]

        for name, func in rules:

            hit, value = func(txn)

            if hit:
                triggered.append(name)
                score += value

        if score >= self.BLOCK_THRESHOLD:
            decision = "BLOCK"

        elif score >= self.REVIEW_THRESHOLD:
            decision = "REVIEW"

        else:
            decision = "PASS"

        return {

            "status": True,

            "transaction_id": txn["TXN_ID"],

            "customer_id": txn["CUSTOMER_ID"],

            "rule_score": score,

            "triggered_rules": triggered,

            "decision": decision

        }
        # =====================================
    # Evaluate All
    # =====================================
    def evaluate_all(self, txn_id):
        """
        Evaluate transaction and return
        overall fraud assessment.
        """

        result = self.evaluate(txn_id)

        if not result["status"]:
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

            "rules": result["triggered_rules"]

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

    engine = RuleEngine()

    result = engine.evaluate_all("TXN005")

    from pprint import pprint

    pprint(result)

    engine.close()