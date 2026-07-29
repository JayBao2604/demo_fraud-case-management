"""
rules/merchant_risk.py
Merchant Risk Rule
"""

from modules.loader import DatabaseLoader


class MerchantRiskRule:

    RULE_ID = "MERCHANT001"
    RULE_NAME = "High Risk Merchant"

    def __init__(self):
        self.db = DatabaseLoader()

    def evaluate(self, transaction):

        merchant = self.db.get_merchant(
            transaction["MERCHANT_ID"]
        )

        if merchant.empty:

            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": False,
                "score": 0,
                "message": "Merchant not found"
            }

        merchant = merchant.iloc[0]

        if merchant["RISK_LEVEL"] == "HIGH":

            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": True,
                "score": 20,
                "message": "High Risk Merchant"
            }

        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": False,
            "score": 0,
            "message": "Normal Merchant"
        }