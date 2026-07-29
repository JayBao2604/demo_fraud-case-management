"""
rules/new_device.py
Detect New Device Rule
"""

class NewDeviceRule:

    RULE_ID = "DEVICE001"
    RULE_NAME = "New Device Detection"

    def evaluate(self, transaction):

        device = str(transaction["DEVICE_ID"]).upper()

        if device == "NEW_DEVICE":

            return {
                "rule_id": self.RULE_ID,
                "rule_name": self.RULE_NAME,
                "triggered": True,
                "score": 20,
                "message": "Transaction from new device."
            }

        return {
            "rule_id": self.RULE_ID,
            "rule_name": self.RULE_NAME,
            "triggered": False,
            "score": 0,
            "message": "Known device."
        }


if __name__ == "__main__":

    txn = {
        "DEVICE_ID": "NEW_DEVICE"
    }

    rule = NewDeviceRule()

    print(rule.evaluate(txn))