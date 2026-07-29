"""
FR025
Velocity + Night Transaction
"""

from rules.velocity import VelocityRule
from rules.night_transaction import NightTransactionRule


class FR025:

    RULE_ID = "FR025"
    RULE_NAME = "Velocity + Night Transaction"

    def __init__(self):

        self.velocity = VelocityRule()

        self.night = NightTransactionRule()

    def evaluate(self, transaction):

        velocity = self.velocity.evaluate(transaction)

        night = self.night.evaluate(transaction)

        if velocity["triggered"] and night["triggered"]:

            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": True,
                "score": 40,
                "message": "Multiple night transactions detected."
            }

        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": False,
            "score": 0,
            "message": "Rule not triggered."
        }