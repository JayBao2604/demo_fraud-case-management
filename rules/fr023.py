"""
FR023
Foreign Country + High Risk Merchant
"""

from rules.foreign_country import ForeignCountryRule
from rules.merchant_risk import MerchantRiskRule


class FR023:

    RULE_ID = "FR023"
    RULE_NAME = "Foreign Country + High Risk Merchant"

    def __init__(self):

        self.country = ForeignCountryRule()

        self.merchant = MerchantRiskRule()

    def evaluate(self, transaction):

        country = self.country.evaluate(transaction)

        merchant = self.merchant.evaluate(transaction)

        if country["triggered"] and merchant["triggered"]:

            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": True,
                "score": 45,
                "message": "Foreign transaction at high-risk merchant."
            }

        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": False,
            "score": 0,
            "message": "Rule not triggered."
        }