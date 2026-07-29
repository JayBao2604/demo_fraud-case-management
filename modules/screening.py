"""
modules/screening.py
---------------------------------------
Sanction / Watchlist Screening
Fraud Lifecycle Management
"""

import pandas as pd

from modules.loader import DatabaseLoader


class Screening:

    # =====================================
    # Configuration
    # =====================================

    HIGH_RISK_CUSTOMER = 50
    AML_HIGH_SCORE = 30
    INCOMPLETE_KYC = 20

    FOREIGN_TRANSACTION = 40
    HIGH_RISK_MERCHANT = 40
    NEW_DEVICE = 20

    def __init__(self):

        self.db = DatabaseLoader()

    # =====================================
    # Risk Level
    # =====================================

    def risk_level(self, score):

        if score >= 70:
            return "HIGH"

        elif score >= 40:
            return "MEDIUM"

        return "LOW"

    # =====================================
    # Recommendation
    # =====================================

    def recommendation(self, level):

        if level == "HIGH":
            return "Reject"

        elif level == "MEDIUM":
            return "Manual Review"

        return "Approved"

    # =====================================
    # Screening Customer
    # =====================================

    def evaluate_customer(self, customer_id):

        customer = self.db.get_customer(customer_id)

        if customer.empty:

            return {

                "status": False,

                "message": "Customer not found"

            }

        customer = customer.iloc[0]

        score = 0
        matches = []

        # --------------------------
        # Risk Rating
        # --------------------------

        if customer["RISK_RATING"] == "HIGH":

            score += self.HIGH_RISK_CUSTOMER

            matches.append("High Risk Customer")

        # --------------------------
        # AML
        # --------------------------

        if int(customer["AML_SCORE"]) >= 80:

            score += self.AML_HIGH_SCORE

            matches.append("High AML Score")

        # --------------------------
        # KYC
        # --------------------------

        if customer["KYC_LEVEL"] in ["BASIC", "PARTIAL"]:

            score += self.INCOMPLETE_KYC

            matches.append("Incomplete KYC")

        level = self.risk_level(score)

        return {

            "status": True,

            "customer_id": customer["CUSTOMER_ID"],

            "full_name": customer["FULL_NAME"],

            "screening_score": score,

            "risk_level": level,

            "matches": matches,

            "recommendation": self.recommendation(level)

        }

    # =====================================
    # Screening Transaction
    # =====================================

    def evaluate_transaction(self, transaction):

        # ---------------------------------
        # Transaction ID
        # ---------------------------------

        if isinstance(transaction, str):

            txn = self.db.get_transaction(transaction)

            if txn.empty:

                return {

                    "status": False,

                    "message": "Transaction not found"

                }

            txn = txn.iloc[0]

        # ---------------------------------
        # Pandas Series
        # ---------------------------------

        elif isinstance(transaction, pd.Series):

            txn = transaction

        else:

            return {

                "status": False,

                "message": "Invalid transaction"

            }

        score = 0
        matches = []

        # --------------------------
        # Foreign Country
        # --------------------------

        if txn["COUNTRY"] != "VN":

            score += self.FOREIGN_TRANSACTION

            matches.append("Foreign Transaction")

        # --------------------------
        # Merchant
        # --------------------------

        merchant = self.db.get_merchant(txn["MERCHANT_ID"])

        if not merchant.empty:

            merchant = merchant.iloc[0]

            if merchant["RISK_LEVEL"] == "HIGH":

                score += self.HIGH_RISK_MERCHANT

                matches.append("High Risk Merchant")

        # --------------------------
        # Device
        # --------------------------

        if txn["DEVICE_ID"] == "NEW_DEVICE":

            score += self.NEW_DEVICE

            matches.append("New Device")

        level = self.risk_level(score)

        return {

            "status": True,

            "transaction_id": txn["TXN_ID"],

            "customer_id": txn["CUSTOMER_ID"],

            "screening_score": score,

            "risk_level": level,

            "matches": matches,

            "recommendation": self.recommendation(level)

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

            level = self.evaluate_transaction(txn)["risk_level"]

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


# =====================================
# Test
# =====================================

if __name__ == "__main__":

    screening = Screening()

    from pprint import pprint

    pprint(screening.evaluate_customer("C001"))

    print()

    pprint(screening.evaluate_transaction("TXN005"))

    print()

    pprint(screening.statistics())

    screening.close()