import streamlit as st
import pandas as pd

from modules.loader import DatabaseLoader
from modules.ekyc import EKYC
from modules.aml import AML
from modules.screening import Screening
from modules.rule_engine import RuleEngine
from modules.alert_engine import AlertEngine
from modules.case_manager import CaseManager

# ============================================
# Page Config
# ============================================

st.set_page_config(
    page_title="Fraud Lifecycle Management",
    page_icon="🛡️",
    layout="wide"
)

# Load Modules

db = DatabaseLoader()
ekyc = EKYC()
aml = AML()
screening = Screening()
rule = RuleEngine()
alert = AlertEngine()
case = CaseManager()

# Title

st.title("🛡️ Fraud Lifecycle Management System")

st.markdown("---")

# Sidebar

st.sidebar.title("Navigation")

menu = st.sidebar.radio(
    "Select Module",
    [
        "Dashboard",
        "Customers",
        "Transactions",
        "Alerts",
        "Cases"
    ]
)

st.sidebar.markdown("---")
st.sidebar.success("Tech Risk Consulting Demo")

# Load Data

customer_df = db.load_customer()
account_df = db.load_account()
card_df = db.load_card()
merchant_df = db.load_merchant()
txn_df = db.load_transaction()

# KPI Dashboard

if menu == "Dashboard":

    st.header("📊 Executive Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Customers",
        len(customer_df)
    )

    c2.metric(
        "Accounts",
        len(account_df)
    )

    c3.metric(
        "Cards",
        len(card_df)
    )

    c4.metric(
        "Transactions",
        len(txn_df)
    )

    st.markdown("---")
    if not txn_df.empty:
        total_amount = txn_df["AMOUNT"].sum()
        fraud = txn_df["FRAUD_LABEL"].sum()
        fraud_rate = round(
            fraud / len(txn_df) * 100,
            2
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Total Amount",
            f"{total_amount:,.0f}"
        )
        c2.metric(
            "Fraud Transactions",
            int(fraud)
        )
        c3.metric(
            "Fraud Rate",
            f"{fraud_rate}%"
        )

    st.markdown("---")
    st.subheader("Latest Transactions")
    st.dataframe(
        txn_df,
        use_container_width=True
    )

    # ============================================
# CUSTOMER PAGE
# ============================================

elif menu == "Customers":
    st.header("👤 Customer Management")
    customer_list = customer_df["CUSTOMER_ID"].tolist()
    customer_id = st.selectbox(
        "Select Customer",
        customer_list
    )
    info = ekyc.evaluate(customer_id)
    st.subheader("eKYC Result")
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Risk Score",
        info["ekyc_score"]
    )
    col2.metric(
        "Risk Level",
        info["ekyc_risk"]
    )
    col3.metric(
        "AML Score",
        info["aml_score"]
    )

    st.markdown("---")
    st.write("### Customer Information")
    st.json(info)
    st.markdown("---")
    st.write("### AML Evaluation")
    aml_result = aml.evaluate_customer(customer_id)
    st.json(aml_result)

# TRANSACTION PAGE

elif menu == "Transactions":
    st.header("💳 Transaction Monitoring")
    transaction_list = txn_df["TXN_ID"].tolist()
    txn_id = st.selectbox(
        "Select Transaction",
        transaction_list
    )

    txn = db.get_transaction(txn_id)
    if not txn.empty:
        txn = txn.iloc[0]
        st.subheader("Transaction Detail")
        st.write(dict(txn))
        st.markdown("---")
        screening_result = screening.evaluate_transaction(txn_id)
        st.subheader("Screening")
        st.json(screening_result)
        st.markdown("---")
        rule_result = rule.evaluate(txn_id)
        st.subheader("Rule Engine")
        st.json(rule_result)
        st.markdown("---")
        if st.button("Generate Alert"):
            result = alert.generate_alert(txn_id)
            st.success("Alert Generated")
            st.json(result)
        st.markdown("---")
        if st.button("Create Investigation Case"):
            case_result = case.create_case(txn_id)
            st.success("Case Created")
            st.json(case_result)
            import matplotlib.pyplot as plt

# ALERT PAGE

elif menu == "Alerts":
    st.header("🚨 Fraud Alerts")
    alerts = alert.get_alerts()

    if len(alerts) == 0:
        st.info("No alerts available.")
    else:
        alert_df = pd.DataFrame(
            alerts,
            columns=[
                "Alert ID",
                "Transaction",
                "Customer",
                "Alert Level",
                "Rule Score",
                "Status",
                "Created Time"
            ]
        )

        st.dataframe(
            alert_df,
            use_container_width=True
        )
        st.markdown("---")

        level_count = (
            alert_df["Alert Level"]
            .value_counts()
        )

        fig = plt.figure(figsize=(5,5))

        plt.pie(
            level_count,
            labels=level_count.index,
            autopct="%1.1f%%"
        )
        plt.title("Alert Distribution")
        st.pyplot(fig)

# CASE PAGE

elif menu == "Cases":
    st.header("📂 Investigation Cases")
    cases = case.get_cases()
    if len(cases) == 0:
        st.info("No cases available.")
    else:

        case_df = pd.DataFrame(
            cases,
            columns=[
                "Case ID",
                "Alert ID",
                "Transaction",
                "Customer",
                "Priority",
                "Assigned To",
                "Status",
                "Created",
                "Closed",
                "Remark"
            ]
        )
        st.dataframe(
            case_df,
            use_container_width=True
        )
        st.markdown("---")
        status_count = (
            case_df["Status"]
            .value_counts()

        )
        fig = plt.figure(figsize=(6,4))
        plt.bar(
            status_count.index,
            status_count.values
        )
        plt.title("Case Status")
        plt.ylabel("Count")
        st.pyplot(fig)
        st.markdown("---")
        open_case = case_df[
            case_df["Status"] == "OPEN"
        ]
        st.subheader("Open Cases")

        st.dataframe(
            open_case,
            use_container_width=True
        )
        st.subheader("Fraud Analytics")

left, right = st.columns(2)
with left:
    risk = txn_df["FRAUD_LABEL"].value_counts()
    fig = plt.figure(figsize=(5,5))
    plt.pie(
        risk,
        labels=["Normal", "Fraud"],
        autopct="%1.1f%%"
    )
    plt.title("Fraud Ratio")

    st.pyplot(fig)

with right:

    merchant = (
        txn_df.groupby("MERCHANT_ID")["AMOUNT"]
        .sum()
    )
    fig = plt.figure(figsize=(7,4))

    plt.bar(
        merchant.index,
        merchant.values
    )
    plt.title("Transaction Amount by Merchant")
    plt.ylabel("Amount")
    st.pyplot(fig)