import streamlit as st
import pandas as pd
import plotly.express as px

from modules.loader import DatabaseLoader
from modules.alert_engine import AlertEngine
from modules.case_manager import CaseManager

# =====================================
# Page Config
# =====================================

st.set_page_config(
    page_title="Fraud Report",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# SECURITY & ACCESS CONTROL
# ==========================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🚫 Access Denied. Please log in at the homepage.")
    st.stop()

def require_role(allowed_roles):
    if st.session_state.role not in allowed_roles:
        st.error(f"🚫 Access Denied: Your role '{st.session_state.role}' does not have permission to access this module.")
        st.stop()

require_role(["USER", "FRAUD", "KSV"])

# =====================================
# Cache Resource
# =====================================

@st.cache_resource
def get_loader():
    return DatabaseLoader()

@st.cache_resource
def get_alert():
    return AlertEngine()

@st.cache_resource
def get_case():
    return CaseManager()

db = get_loader()
alert_engine = get_alert()
case_manager = get_case()

# =====================================
# Load Data
# =====================================

@st.cache_data(ttl=10)
def load_data():

    txn = db.load_transaction()
    customer = db.load_customer()

    try:
        merchant = db.load_merchant()
    except:
        merchant = pd.DataFrame()

    try:
        result = alert_engine.get_alerts()

        if isinstance(result, dict):
            alerts = result.get("alerts", pd.DataFrame())
        else:
            alerts = result

    except:
        alerts = pd.DataFrame()

    try:
        result = case_manager.get_cases()

        if isinstance(result, dict):
            cases = result.get("cases", pd.DataFrame())
        else:
            cases = result

    except:
        cases = pd.DataFrame()

    return (
        txn,
        customer,
        merchant,
        alerts,
        cases
    )

txn, customer, merchant, alerts, cases = load_data()

# ---------------------------------------------------------
# FIX: Đảm bảo dữ liệu luôn là DataFrame để tránh lỗi .empty
# ---------------------------------------------------------
if not isinstance(alerts, pd.DataFrame):
    alerts = pd.DataFrame(alerts)

if not isinstance(cases, pd.DataFrame):
    cases = pd.DataFrame(cases)

if not isinstance(txn, pd.DataFrame):
    txn = pd.DataFrame(txn)

if not isinstance(customer, pd.DataFrame):
    customer = pd.DataFrame(customer)


st.title("📊 Fraud Lifecycle Report")

# =====================================
# Sidebar
# =====================================

st.sidebar.header("Report Filter")

# Kiểm tra xem có cột COUNTRY không trước khi lọc
if not txn.empty and "COUNTRY" in txn.columns:
    country = st.sidebar.multiselect(
        "Country",
        sorted(txn["COUNTRY"].dropna().unique()),
        default=sorted(txn["COUNTRY"].dropna().unique())
    )

    if country:
        txn = txn[
            txn["COUNTRY"].isin(country)
        ]

# =====================================
# KPI
# =====================================

st.subheader("📈 Executive Dashboard")

fraud = pd.DataFrame()

if not txn.empty and "FRAUD_LABEL" in txn.columns:
    fraud = txn[
        txn["FRAUD_LABEL"] == 1
    ]

total_amount = 0

if not txn.empty and "AMOUNT" in txn.columns:
    total_amount = txn["AMOUNT"].sum()

fraud_rate = 0

if len(txn) > 0:
    fraud_rate = len(fraud) / len(txn) * 100

k1,k2,k3,k4 = st.columns(4)

k1.metric(
    "Transactions",
    len(txn)
)

k2.metric(
    "Customers",
    len(customer)
)

k3.metric(
    "Alerts",
    len(alerts)
)

k4.metric(
    "Cases",
    len(cases)
)

k5,k6,k7 = st.columns(3)

k5.metric(
    "Fraud Rate",
    f"{fraud_rate:.2f}%"
)

k6.metric(
    "Fraud Txns",
    len(fraud)
)

k7.metric(
    "Total Amount",
    f"{total_amount:,.0f} VND"
)

st.divider()

# =====================================
# Alert Analysis
# =====================================

st.subheader("🚨 Alert Analysis")

if alerts.empty:
    st.info("No alert data available.")
else:
    col1, col2 = st.columns(2)

    with col1:
        if "ALERT_LEVEL" in alerts.columns:
            alert_level = (
                alerts["ALERT_LEVEL"]
                .value_counts()
                .reset_index()
            )
            alert_level.columns = [
                "Alert Level",
                "Count"
            ]

            fig = px.bar(
                alert_level,
                x="Alert Level",
                y="Count",
                color="Alert Level",
                title="Alert Level Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    with col2:
        if "STATUS" in alerts.columns:
            alert_status = (
                alerts["STATUS"]
                .value_counts()
                .reset_index()
            )
            alert_status.columns = [
                "Status",
                "Count"
            ]

            fig = px.pie(
                alert_status,
                names="Status",
                values="Count",
                title="Alert Status"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

st.divider()

# =====================================
# Case Analysis
# =====================================

st.subheader("📂 Case Analysis")

if cases.empty:
    st.info("No investigation case available.")
else:
    col1, col2 = st.columns(2)

    with col1:
        if "STATUS" in cases.columns:
            case_status = (
                cases["STATUS"]
                .value_counts()
                .reset_index()
            )
            case_status.columns = [
                "Status",
                "Count"
            ]

            fig = px.bar(
                case_status,
                x="Status",
                y="Count",
                color="Status",
                title="Case Status Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    with col2:
        if "RISK_SCORE" in cases.columns:
            fig = px.histogram(
                cases,
                x="RISK_SCORE",
                nbins=10,
                title="Case Risk Score Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

st.divider()

# =====================================
# Fraud Transactions
# =====================================

st.subheader("🚨 Fraud Transaction List")

if fraud.empty:
    st.info("No fraud transaction detected.")
else:
    fraud_display = fraud.rename(columns={
        "TXN_ID":"Transaction ID",
        "CARD_ID":"Card ID",
        "CUSTOMER_ID":"Customer ID",
        "MERCHANT_ID":"Merchant ID",
        "TERMINAL_ID":"Terminal",
        "TXN_TIME":"Transaction Time",
        "AMOUNT":"Amount (VND)",
        "COUNTRY":"Country",
        "DEVICE_ID":"Device",
        "FRAUD_LABEL":"Fraud"
    })

    st.dataframe(
        fraud_display,
        use_container_width=True,
        hide_index=True,
        height=350
    )

st.divider()

# =====================================
# Alert List
# =====================================

st.subheader("🚨 Alert List")

if alerts.empty:
    st.info("No alerts.")
else:
    st.dataframe(
        alerts,
        use_container_width=True,
        hide_index=True,
        height=300
    )

st.divider()

# =====================================
# Investigation Cases
# =====================================

st.subheader("📂 Investigation Cases")

if cases.empty:
    st.info("No cases.")
else:
    st.dataframe(
        cases,
        use_container_width=True,
        hide_index=True,
        height=300
    )

st.divider()

# =====================================
# Export Report
# =====================================

st.subheader("📤 Export Report")

col1, col2, col3 = st.columns(3)

with col1:
    if not txn.empty:
        csv_txn = txn.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Transaction Report",
            data=csv_txn,
            file_name="transaction_report.csv",
            mime="text/csv",
            use_container_width=True
        )

with col2:
    if not alerts.empty:
        csv_alert = alerts.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Alert Report",
            data=csv_alert,
            file_name="alert_report.csv",
            mime="text/csv",
            use_container_width=True
        )

with col3:
    if not cases.empty:
        csv_case = cases.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Case Report",
            data=csv_case,
            file_name="case_report.csv",
            mime="text/csv",
            use_container_width=True
        )

st.divider()

# =====================================
# Executive Summary
# =====================================

st.subheader("📋 Executive Summary")

summary = pd.DataFrame({
    "Metric":[
        "Total Transactions",
        "Fraud Transactions",
        "Fraud Rate (%)",
        "Total Customers",
        "Total Alerts",
        "Total Cases",
        "Transaction Amount"
    ],
    "Value":[
        len(txn),
        len(fraud),
        round(fraud_rate,2),
        len(customer),
        len(alerts),
        len(cases),
        f"{total_amount:,.0f} VND"
    ]
})

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)

st.divider()

# =====================================
# Refresh Report
# =====================================

col1, col2 = st.columns([1,4])

with col1:
    if st.button(
        "🔄 Refresh",
        use_container_width=True
    ):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.info(
        "Refresh the report after generating new alerts or investigation cases."
    )

st.divider()

# =====================================
# Generated Information
# =====================================

st.caption("Fraud Lifecycle Management System")
st.caption("Demo")
st.caption("Generated by Streamlit Dashboard")

st.success("✅ Report generated successfully.")