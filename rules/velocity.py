"""
rules/velocity.py
Velocity Rule
"""

from modules.loader import DatabaseLoader


class VelocityRule:

    RULE_ID = "VELOCITY001"
    RULE_NAME = "Transaction Velocity"

    def __init__(self):

        self.db = DatabaseLoader()

    def evaluate(self, transaction):

        df = self.db.load_transaction()

        customer = transaction["CUSTOMER_ID"]

        customer_txn = df[
            df["CUSTOMER_ID"] == customer
        ]

        count = len(customer_txn)

        if count >= 10:

            score = 35

        elif count >= 5:

            score = 20

        else:

            score = 0

        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": score > 0,
            "score": score,
            "message": f"{count} transactions detected"
        }