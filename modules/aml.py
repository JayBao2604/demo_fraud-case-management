"""
modules/aml.py
---------------------------------------
Anti-Money Laundering (AML)
Fraud Lifecycle Management
"""

import pandas as pd

from modules.loader import DatabaseLoader
from modules.ekyc import EKYC


class AML:

    # =====================================
    # Configuration
    # =====================================

    LARGE_AMOUNT = 10_000_000

    SCORE_AMOUNT = 30
    SCORE_FOREIGN = 30
    SCORE_NEW_DEVICE = 20
    SCORE_HIGH_RISK_MERCHANT = 20

    def __init__(self):

        self.db = DatabaseLoader()
        self.ekyc = EKYC()

    # =====================================
    # Get Customer
    # =====================================

    def get_customer(self, customer_id):

        customer = self.db.get_customer(customer_id)

        if customer.empty:
            return None

        return customer.iloc[0]

    # =====================================
    # AML Risk Level
    # =====================================

    def risk_level(self, score):

        if score >= 80:
            return "HIGH"

        elif score >= 50:
            return "MEDIUM"

        return "LOW"

    # =====================================
    # Recommendation
    # =====================================

    def recommendation(self, level):

        if level == "HIGH":
            return "Enhanced Due Diligence"

        elif level == "MEDIUM":
            return "Manual Review"

        return "Approve"

    # =====================================
    # Customer AML
    # =====================================

    def evaluate_customer(self, customer_id):

        customer = self.get_customer(customer_id)

        if customer is None:

            return {

                "status": False,

                "message": "Customer not found"

            }

        ekyc = self.ekyc.evaluate(customer_id)

        aml_score = int(customer["AML_SCORE"])

        risk = self.risk_level(aml_score)

        return {

            "status": True,

            "customer_id": customer["CUSTOMER_ID"],

            "full_name": customer["FULL_NAME"],

            "aml_score": aml_score,

            "aml_risk": risk,

            "ekyc_score": ekyc.get("ekyc_score", 0),

            "ekyc_risk": ekyc.get("ekyc_risk", "LOW"),

            "recommendation": self.recommendation(risk)

        }

    # =====================================
    # Monitor Transaction
    # =====================================

    def monitor_transaction(self, txn):

        score = 0

        if txn["AMOUNT"] >= self.LARGE_AMOUNT:
            score += self.SCORE_AMOUNT

        if txn["COUNTRY"] != "VN":
            score += self.SCORE_FOREIGN

        if txn["DEVICE_ID"] == "NEW_DEVICE":
            score += self.SCORE_NEW_DEVICE

        merchant = self.db.get_merchant(txn["MERCHANT_ID"])

        if not merchant.empty:

            merchant = merchant.iloc[0]

            if merchant["RISK_LEVEL"] == "HIGH":

                score += self.SCORE_HIGH_RISK_MERCHANT

        return {

            "risk_score": score,

            "risk_level": self.risk_level(score)

        }

    # =====================================
    # Transaction AML
    # =====================================

    def evaluate_transaction(self, transaction):

        if isinstance(transaction, str):

            txn = self.db.get_transaction(transaction)

            if txn.empty:

                return {

                    "status": False,

                    "message": "Transaction not found"

                }

            txn = txn.iloc[0]

        elif isinstance(transaction, pd.Series):

            txn = transaction

        else:

            return {

                "status": False,

                "message": "Invalid transaction"

            }

        result = self.monitor_transaction(txn)

        return {

            "status": True,

            "transaction_id": txn["TXN_ID"],

            "customer_id": txn["CUSTOMER_ID"],

            "merchant_id": txn["MERCHANT_ID"],

            "amount": txn["AMOUNT"],

            "country": txn["COUNTRY"],

            "device": txn["DEVICE_ID"],

            "risk_score": result["risk_score"],

            "risk_level": result["risk_level"]

        }

    # =====================================
    # Statistics
    # =====================================

    def statistics(self):

        transactions = self.db.load_transaction()

        total = len(transactions)

        high = 0
        medium = 0
        low = 0

        for _, txn in transactions.iterrows():

            level = self.monitor_transaction(txn)["risk_level"]

            if level == "HIGH":
                high += 1

            elif level == "MEDIUM":
                medium += 1

            else:
                low += 1

        return {

            "total_transaction": total,

            "high_risk": high,

            "medium_risk": medium,

            "low_risk": low

        }

    # =====================================
    # Close
    # =====================================

    def close(self):

        self.db.close()
        self.ekyc.close()


if __name__ == "__main__":

    aml = AML()

    from pprint import pprint

    pprint(aml.evaluate_customer("C001"))

    print()

    pprint(aml.evaluate_transaction("TXN001"))

    print()

    pprint(aml.statistics())

    aml.close()