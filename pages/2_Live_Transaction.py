import streamlit as st
import pandas as pd

from modules.loader import DatabaseLoader
from modules.ekyc import EKYC
from modules.aml import AML
from modules.screening import Screening
from modules.rule_engine import RuleEngine
from modules.alert_engine import AlertEngine
from modules.case_manager import CaseManager

# =====================================
# Page Config
# =====================================

st.set_page_config(
    page_title="Live Transaction",
    page_icon="💳",
    layout="wide"
)

# =====================================
# Cache Resource
# =====================================

@st.cache_resource
def get_loader():
    return DatabaseLoader()

@st.cache_resource
def get_ekyc():
    return EKYC()

@st.cache_resource
def get_aml():
    return AML()

@st.cache_resource
def get_screen():
    return Screening()

@st.cache_resource
def get_rule():
    return RuleEngine()

@st.cache_resource
def get_alert():
    return AlertEngine()

@st.cache_resource
def get_case():
    return CaseManager()


db = get_loader()
ekyc = get_ekyc()
aml = get_aml()
screen = get_screen()
rule_engine = get_rule()
alert_engine = get_alert()
case_manager = get_case()

# =====================================
# Load Transactions
# =====================================

@st.cache_data(ttl=10)
def load_transactions():
    return db.load_transaction()

transactions = load_transactions()

st.title("💳 Live Transaction Monitoring")

if transactions.empty:

    st.warning("No transaction found.")

    st.stop()

# =====================================
# Sidebar
# =====================================

st.sidebar.header("Transaction Filter")

txn_id = st.sidebar.selectbox(

    "Transaction",

    transactions["TXN_ID"]

)

# =====================================
# Load Transaction
# =====================================

transaction = db.get_transaction(txn_id)

if transaction.empty:

    st.error("Transaction not found.")

    st.stop()

txn = transaction.iloc[0]

# =====================================
# Transaction Information
# =====================================

st.subheader("📄 Transaction Information")

left, right = st.columns(2)

with left:

    st.metric(

        "Transaction ID",

        txn["TXN_ID"]

    )

    st.metric(

        "Customer",

        txn["CUSTOMER_ID"]

    )

    st.metric(

        "Merchant",

        txn["MERCHANT_ID"]

    )

    st.metric(

        "Amount",

        f"{txn['AMOUNT']:,.0f}"

    )

with right:

    st.metric(

        "Country",

        txn["COUNTRY"]

    )

    st.metric(

        "Device",

        txn["DEVICE_ID"]

    )

    if "TERMINAL_ID" in txn.index:

        st.metric(

            "Terminal",

            txn["TERMINAL_ID"]

        )

    st.metric(

        "Transaction Time",

        str(txn["TXN_TIME"])

    )

st.divider()

# =====================================
# Customer Information
# =====================================

customer = db.get_customer(

    txn["CUSTOMER_ID"]

)

if not customer.empty:

    customer = customer.iloc[0]

    st.subheader("👤 Customer")

    c1, c2, c3 = st.columns(3)

    c1.metric(

        "Customer Name",

        customer["FULL_NAME"]

    )

    c2.metric(

        "Risk Rating",

        customer["RISK_RATING"]

    )

    c3.metric(

        "AML Score",

        customer["AML_SCORE"]

    )

st.divider()
# =====================================
# Risk Analysis
# =====================================

st.subheader("🛡 Risk Analysis")

col1, col2, col3 = st.columns(3)

# =====================================
# eKYC
# =====================================

with col1:

    st.markdown("### 🪪 eKYC")

    try:

        ekyc_result = ekyc.evaluate(
            txn["CUSTOMER_ID"]
        )

        st.metric(
            "eKYC Score",
            ekyc_result.get("ekyc_score", 0)
        )

        st.metric(
            "Risk",
            ekyc_result.get("ekyc_risk", "-")
        )

        st.metric(
            "KYC Level",
            ekyc_result.get("kyc_level", "-")
        )

        st.write(
            "**Recommendation:**",
            ekyc_result.get(
                "recommendation",
                "-"
            )
        )

    except Exception as e:

        st.error(e)

# =====================================
# AML
# =====================================

with col2:

    st.markdown("### 🏦 AML")

    try:

        aml_result = aml.evaluate_transaction(
            txn
        )

        st.metric(
            "AML Score",
            aml_result["risk_score"]
        )

        st.metric(
            "Risk",
            aml_result["risk_level"]
        )

        st.metric(
            "Country",
            aml_result["country"]
        )

    except Exception as e:

        st.error(e)

# =====================================
# Screening
# =====================================

with col3:

    st.markdown("### 🔍 Screening")

    try:

        screening = screen.evaluate_transaction(
            txn
        )

        st.metric(
            "Score",
            screening["screening_score"]
        )

        st.metric(
            "Risk",
            screening["risk_level"]
        )

        st.write("Matches")

        matches = screening.get(
            "matches",
            []
        )

        if matches:

            for m in matches:

                st.success(m)

        else:

            st.info("No Match")

    except Exception as e:

        st.error(e)

st.divider()

# =====================================
# Rule Engine
# =====================================

st.subheader("⚙ Rule Engine")

rule_result = rule_engine.evaluate_all(
    txn["TXN_ID"]
)

if rule_result["status"]:

    c1, c2, c3 = st.columns(3)

    c1.metric(

        "Rule Score",

        rule_result["score"]

    )

    c2.metric(

        "Risk",

        rule_result["risk"]

    )

    c3.metric(

        "Decision",

        rule_result["decision"]

    )

    if rule_result["decision"] == "BLOCK":

        st.error("🚫 BLOCK")

    elif rule_result["decision"] == "REVIEW":

        st.warning("🟡 REVIEW")

    else:

        st.success("🟢 PASS")

    st.write("### Triggered Rules")

    rules = rule_result.get(
        "rules",
        []
    )

    if len(rules):

        df = pd.DataFrame({

            "Rule": rules

        })

        st.dataframe(

            df,

            use_container_width=True

        )

    else:

        st.success(
            "No rule triggered."
        )

else:

    st.error(
        rule_result["message"]
    )

st.divider()

# =====================================
# Overall Risk Summary
# =====================================

st.subheader("📊 Overall Risk Summary")

summary = pd.DataFrame({

    "Module": [

        "eKYC",

        "AML",

        "Screening",

        "Rule Engine"

    ],

    "Risk": [

        ekyc_result.get("ekyc_risk"),

        aml_result.get("risk_level"),

        screening.get("risk_level"),

        rule_result.get("risk")

    ]

})

st.dataframe(

    summary,

    use_container_width=True

)
# =====================================
# Alert & Case Management
# =====================================

st.subheader("🚨 Alert & Investigation")

col1, col2 = st.columns(2)

# =====================================
# Generate Alert
# =====================================

with col1:

    if st.button(
        "🚨 Generate Alert",
        use_container_width=True
    ):

        try:

            result = alert_engine.generate_alert(
                txn["TXN_ID"]
            )

            if result["status"]:

                st.success(result["message"])

                if "alert" in result:

                    st.json(result["alert"])

            else:

                st.warning(result["message"])

        except Exception as e:

            st.error(e)

# =====================================
# Create Case
# =====================================

with col2:

    if st.button(
        "📂 Create Investigation Case",
        use_container_width=True
    ):

        try:

            result = case_manager.create_case(
                txn["TXN_ID"]
            )

            if result["status"]:

                st.success(result["message"])

                if "case" in result:

                    st.json(result["case"])

            else:

                st.warning(result["message"])

        except Exception as e:

            st.error(e)

st.divider()

# =====================================
# Current Alert
# =====================================

st.subheader("🚨 Current Alert")

try:

    alert = alert_engine.get_alert(
        txn["TXN_ID"]
    )

    if isinstance(alert, dict):

        if alert.get("status"):

            st.dataframe(

                pd.DataFrame([

                    alert["alert"]

                ]),

                use_container_width=True

            )

        else:

            st.info(
                "No alert for this transaction."
            )

    elif isinstance(alert, pd.DataFrame):

        if alert.empty:

            st.info(
                "No alert for this transaction."
            )

        else:

            st.dataframe(
                alert,
                use_container_width=True
            )

except Exception as e:

    st.info("No alert found.")

st.divider()

# =====================================
# Current Case
# =====================================

st.subheader("📂 Investigation Case")

try:

    case = case_manager.get_case(
        txn["TXN_ID"]
    )

    if isinstance(case, dict):

        if case.get("status"):

            st.dataframe(

                pd.DataFrame([

                    case["case"]

                ]),

                use_container_width=True

            )

        else:

            st.info(
                "No case for this transaction."
            )

    elif isinstance(case, pd.DataFrame):

        if case.empty:

            st.info(
                "No case for this transaction."
            )

        else:

            st.dataframe(
                case,
                use_container_width=True
            )

except Exception:

    st.info("No case found.")

st.divider()

# =====================================
# Related Transactions
# =====================================

st.subheader("💳 Customer Transaction History")

try:

    history = db.get_transactions_by_customer(
        txn["CUSTOMER_ID"]
    )

    if not history.empty:

        history = history.sort_values(
            "TXN_TIME",
            ascending=False
        )

        st.dataframe(

            history,

            use_container_width=True,

            height=300

        )

    else:

        st.info(
            "No previous transaction."
        )

except Exception as e:

    st.error(e)

st.divider()

# =====================================
# Card History
# =====================================

st.subheader("💳 Card Transaction History")

try:

    history = db.get_transactions_by_card(
        txn["CARD_ID"]
    )

    if not history.empty:

        history = history.sort_values(
            "TXN_TIME",
            ascending=False
        )

        st.dataframe(

            history,

            use_container_width=True,

            height=300

        )

    else:

        st.info(
            "No transaction history."
        )

except Exception:

    pass

st.divider()