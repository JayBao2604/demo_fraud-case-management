"""
modules/ekyc.py
------------------------------------
Electronic Know Your Customer (eKYC)
Fraud Lifecycle Management
"""

from modules.loader import DatabaseLoader


class EKYC:

    # =====================================
    # Configuration
    # =====================================

    PARTIAL_KYC_SCORE = 30

    AML_HIGH = 40
    AML_MEDIUM = 20
    AML_LOW = 5

    RISK_HIGH = 30
    RISK_MEDIUM = 15
    RISK_LOW = 5

    def __init__(self):

        self.db = DatabaseLoader()

    # =====================================
    # Verify Customer
    # =====================================

    def verify_customer(self, customer_id):

        customer = self.db.get_customer(customer_id)

        if customer.empty:

            return {

                "status": False,

                "message": "Customer not found."

            }

        customer = customer.iloc[0]

        return {

            "status": True,

            "customer_id": customer["CUSTOMER_ID"],

            "full_name": customer["FULL_NAME"],

            "kyc_level": customer["KYC_LEVEL"],

            "aml_score": customer["AML_SCORE"],

            "risk_rating": customer["RISK_RATING"]

        }

    # =====================================
    # Calculate Score
    # =====================================

    def calculate_risk_score(self, customer_id):

        customer = self.db.get_customer(customer_id)

        if customer.empty:
            return None

        customer = customer.iloc[0]

        score = 0

        # -----------------------------
        # KYC Level
        # -----------------------------

        if customer["KYC_LEVEL"] == "PARTIAL":

            score += self.PARTIAL_KYC_SCORE

        # -----------------------------
        # AML
        # -----------------------------

        aml = customer["AML_SCORE"]

        if aml >= 80:

            score += self.AML_HIGH

        elif aml >= 60:

            score += self.AML_MEDIUM

        else:

            score += self.AML_LOW

        # -----------------------------
        # Risk Rating
        # -----------------------------

        rating = customer["RISK_RATING"]

        if rating == "HIGH":

            score += self.RISK_HIGH

        elif rating == "MEDIUM":

            score += self.RISK_MEDIUM

        else:

            score += self.RISK_LOW

        return min(score, 100)

    # =====================================
    # Risk Level
    # =====================================

    def risk_level(self, score):

        if score is None:

            return "UNKNOWN"

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

            return "Enhanced Due Diligence (EDD)"

        elif level == "MEDIUM":

            return "Manual Review"

        return "Approved"

    # =====================================
    # Evaluate
    # =====================================

    def evaluate(self, customer_id):

        info = self.verify_customer(customer_id)

        if not info["status"]:

            return info

        score = self.calculate_risk_score(customer_id)

        level = self.risk_level(score)

        info["ekyc_score"] = score

        info["ekyc_risk"] = level

        info["recommendation"] = self.recommendation(level)

        return info

    # =====================================
    # Statistics
    # =====================================

    def statistics(self):

        customers = self.db.load_customer()

        total = len(customers)

        high = 0
        medium = 0
        low = 0

        for cid in customers["CUSTOMER_ID"]:

            score = self.calculate_risk_score(cid)

            level = self.risk_level(score)

            if level == "HIGH":
                high += 1

            elif level == "MEDIUM":
                medium += 1

            else:
                low += 1

        return {

            "total_customer": total,

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

    ekyc = EKYC()

    print(ekyc.evaluate("C001"))

    print()

    print(ekyc.statistics())

    ekyc.close()