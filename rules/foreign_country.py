"""
rules/foreign_country.py
Foreign Country Rule
"""

class ForeignCountryRule:

    RULE_ID = "COUNTRY001"
    RULE_NAME = "Foreign Transaction"

    HOME_COUNTRY = "VN"

    HIGH_RISK = [
        "IR",
        "KP",
        "SY",
        "AF",
        "RU",
        "NG"
    ]

    def evaluate(self, transaction):

        country = str(transaction["COUNTRY"]).upper()

        if country in self.HIGH_RISK:

            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": True,
                "score": 30,
                "message": f"High Risk Country : {country}"
            }

        if country != self.HOME_COUNTRY:

            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": True,
                "score": 15,
                "message": f"Foreign Transaction : {country}"
            }

        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": False,
            "score": 0,
            "message": "Domestic Transaction"
        }


if __name__ == "__main__":

    txn = {
        "COUNTRY": "HK"
    }

    rule = ForeignCountryRule()

    print(rule.evaluate(txn))