"""
rules/amount.py
Amount Threshold Rule
"""

class AmountRule:

    RULE_ID = "AMOUNT001"
    RULE_NAME = "Large Amount Transaction"

    def __init__(self, threshold=10000000):
        self.threshold = threshold

    def evaluate(self, transaction):

        amount = float(transaction["AMOUNT"])

        if amount >= self.threshold:
            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": True,
                "score": 30,
                "message": f"Amount {amount:,.0f} exceeds threshold {self.threshold:,.0f}"
            }

        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": False,
            "score": 0,
            "message": "Normal transaction amount"
        }


if __name__ == "__main__":

    sample = {
        "AMOUNT": 35000000
    }

    rule = AmountRule()

    print(rule.evaluate(sample))