"""
FR001
Large Amount + New Device
"""

from rules.amount import AmountRule
from rules.new_device import NewDeviceRule


class FR001:

    RULE_ID = "FR001"
    RULE_NAME = "Large Amount + New Device"

    def __init__(self):

        self.amount = AmountRule()

        self.device = NewDeviceRule()

    def evaluate(self, transaction):

        amount = self.amount.evaluate(transaction)

        device = self.device.evaluate(transaction)

        if amount["triggered"] and device["triggered"]:

            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": True,
                "score": 50,
                "message": "Large amount from a new device."
            }

        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": False,
            "score": 0,
            "message": "Rule not triggered."
        }