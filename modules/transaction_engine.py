"""
modules/transaction_engine.py
----------------------------------------
Transaction Monitoring Engine
Fraud Lifecycle Management
"""

from modules.loader import DatabaseLoader
from modules.ekyc import EKYC
from modules.aml import AML
from modules.screening import Screening


class TransactionEngine:

    def __init__(self):
        self.db = DatabaseLoader()
        self.ekyc = EKYC()
        self.aml = AML()
        self.screening = Screening()

    # Load Transaction

    def get_transaction(self, txn_id):

        txn = self.db.get_transaction(txn_id)

        if txn.empty:
            return None

        return txn.iloc[0]

    # Transaction Analysis

    def analyze(self, txn_id):

        txn = self.get_transaction(txn_id)

        if txn is None:
            return {
                "status": False,
                "message": "Transaction not found"
            }

        ekyc_result = self.ekyc.evaluate(
            txn["CUSTOMER_ID"]
        )

        aml_result = self.aml.evaluate_transaction(
            txn["TXN_ID"]
        )

        screening_result = self.screening.evaluate_transaction(
            txn["TXN_ID"]
        )

        return {
            "status": True,

            "transaction": {
                "txn_id": txn["TXN_ID"],
                "customer_id": txn["CUSTOMER_ID"],
                "merchant_id": txn["MERCHANT_ID"],
                "amount": float(txn["AMOUNT"]),
                "country": txn["COUNTRY"],
                "device": txn["DEVICE_ID"]
            },

            "ekyc": ekyc_result,

            "aml": aml_result,

            "screening": screening_result
        }

    # =====================================
    # Monitoring Decision
    # =====================================

    def monitoring_result(self, txn_id):

        result = self.analyze(txn_id)

        if result["status"] is False:
            return result

        score = 0

        score += result["ekyc"]["ekyc_score"]
        score += result["aml"]["risk_score"]
        score += result["screening"]["screening_score"]

        score = round(score / 3)

        if score >= 80:
            decision = "BLOCK"

        elif score >= 50:
            decision = "REVIEW"

        else:
            decision = "PASS"

        result["overall_score"] = score
        result["decision"] = decision

        return result

    # =====================================
    # Close
    # =====================================

    def close(self):

        self.db.close()
        self.ekyc.close()
        self.aml.close()
        self.screening.close()


# =====================================
# Test
# =====================================

if __name__ == "__main__":

    engine = TransactionEngine()

    result = engine.monitoring_result("TXN005")

    from pprint import pprint

    pprint(result)

    engine.close()