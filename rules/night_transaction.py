"""
rules/night_transaction.py
Night Transaction Rule
"""

from datetime import datetime


class NightTransactionRule:

    RULE_ID = "TIME001"
    RULE_NAME = "Night Transaction"

    def evaluate(self, transaction):

        txn_time = datetime.strptime(
            transaction["TXN_TIME"],
            "%Y-%m-%d %H:%M:%S"
        )

        hour = txn_time.hour

        if hour < 6 or hour >= 23:

            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": True,
                "score": 15,
                "message": "Night Transaction"
            }

        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": False,
            "score": 0,
            "message": "Business Hour"
        }