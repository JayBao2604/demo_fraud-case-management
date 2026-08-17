import streamlit as st
import pandas as pd
import plotly.express as px

from modules.loader import DatabaseLoader
from modules.alert_engine import AlertEngine
from modules.case_manager import CaseManager
from modules.aml import AML
from modules.ekyc import EKYC
from modules.screening import Screening

# ======================================
# Page Config
# ======================================

st.set_page_config(
    page_title="Fraud Lifecycle Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ======================================
# Cache Resources
# ======================================

@st.cache_resource
def get_loader():
    return DatabaseLoader()

@st.cache_resource
def get_alert():
    return AlertEngine()

@st.cache_resource
def get_case():
    return CaseManager()

@st.cache_resource
def get_aml():
    return AML()

@st.cache_resource
def get_ekyc():
    return EKYC()

@st.cache_resource
def get_screen():
    return Screening()

db = get_loader()
alert_engine = get_alert()
case_manager = get_case()
aml = get_aml()
ekyc = get_ekyc()
screen = get_screen()

# ======================================
# Load Data
# ======================================

@st.cache_data(ttl=10)
def load_data():

    return {
        "customer": db.load_customer(),
        "account": db.load_account(),
        "card": db.load_card(),
        "merchant": db.load_merchant(),
        "transaction": db.load_transaction()
    }

data = load_data()

customer_df = data["customer"]
account_df = data["account"]
card_df = data["card"]
merchant_df = data["merchant"]
txn_df = data["transaction"]

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

# ======================================
# Sidebar
# ======================================

st.sidebar.title("⚙ Dashboard")

st.sidebar.markdown("### Dataset")

st.sidebar.write(f"Customers : {len(customer_df)}")
st.sidebar.write(f"Accounts : {len(account_df)}")
st.sidebar.write(f"Cards : {len(card_df)}")
# Hiển thị tổng số giao dịch thực tế trong DB
st.sidebar.write(f"Total Transactions : {len(txn_df)}") 

st.sidebar.divider()

show_latest = st.sidebar.slider(
    "Latest Transactions",
    5,
    50,
    10
)

# ======================================
# Lọc Dữ Liệu Theo Thanh Trượt
# ======================================
if not txn_df.empty:
    # Ưu tiên sắp xếp theo thời gian giao dịch mới nhất
    if "TXN_TIME" in txn_df.columns:
        txn_df = txn_df.sort_values("TXN_TIME", ascending=False)
    
    # Cắt dataframe theo số lượng hiển thị từ slider
    txn_df = txn_df.head(show_latest)

# ======================================
# Header
# ======================================

st.title("🛡 Fraud Lifecycle Management Dashboard")

st.caption("Tech Risk Consulting Demo")

st.divider()

# ======================================
# KPI
# ======================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Customers", len(customer_df))
col2.metric("Accounts", len(account_df))
col3.metric("Cards", len(card_df))
col4.metric("Filtered Transactions", len(txn_df)) # Đổi tên cho rõ nghĩa

# ======================================
# Amount KPI
# ======================================

total_amount = 0

if not txn_df.empty:
    total_amount = txn_df["AMOUNT"].sum()

fraud_count = 0

if "FRAUD_LABEL" in txn_df.columns:
    fraud_count = len(
        txn_df[
            txn_df["FRAUD_LABEL"] == 1
        ]
    )

fraud_rate = 0

if len(txn_df):
    fraud_rate = fraud_count / len(txn_df) * 100

c1, c2, c3 = st.columns(3)

c1.metric("Total Amount", f"{total_amount:,.0f}")
c2.metric("Fraud Transactions", fraud_count)
c3.metric("Fraud Rate", f"{fraud_rate:.2f}%")

# ======================================
# Alert & Case KPI
# ======================================

try:
    alerts = alert_engine.get_alerts()
    if isinstance(alerts, list):
        alert_df = pd.DataFrame(alerts)
    else:
        alert_df = alerts
except Exception:
    alert_df = pd.DataFrame()

try:
    case_df = case_manager.get_cases()
except Exception:
    case_df = pd.DataFrame()


alert_total = len(alert_df)
alert_open = 0
alert_closed = 0

if not alert_df.empty:
    if "STATUS" in alert_df.columns:
        alert_open = len(
            alert_df[
                alert_df["STATUS"] == "OPEN"
            ]
        )
        alert_closed = len(
            alert_df[
                alert_df["STATUS"] == "CLOSED"
            ]
        )


case_total = len(case_df)
case_open = 0
case_closed = 0

if not case_df.empty:
    if "STATUS" in case_df.columns:
        case_open = len(
            case_df[
                case_df["STATUS"] == "OPEN"
            ]
        )
        case_closed = len(
            case_df[
                case_df["STATUS"] == "CLOSED"
            ]
        )


st.divider()

st.subheader("🚨 Alert & Investigation Summary")

a1, a2, a3 = st.columns(3)

a1.metric("Total Alerts", alert_total)
a2.metric("Open Alerts", alert_open)
a3.metric("Closed Alerts", alert_closed)

b1, b2, b3 = st.columns(3)

b1.metric("Total Cases", case_total)
b2.metric("Open Cases", case_open)
b3.metric("Closed Cases", case_closed)

# ======================================
# AML Summary
# ======================================

st.divider()

st.subheader("🏦 AML Summary")

aml_high = 0
aml_medium = 0
aml_low = 0

for cid in customer_df["CUSTOMER_ID"]:
    result = aml.evaluate_customer(cid)
    if result["status"]:
        if result["aml_risk"] == "HIGH":
            aml_high += 1
        elif result["aml_risk"] == "MEDIUM":
            aml_medium += 1
        else:
            aml_low += 1

c1, c2, c3 = st.columns(3)

c1.metric("High AML", aml_high)
c2.metric("Medium AML", aml_medium)
c3.metric("Low AML", aml_low)

# ======================================
# eKYC Summary
# ======================================

st.divider()

st.subheader("🪪 eKYC Summary")

ekyc_high = 0
ekyc_medium = 0
ekyc_low = 0

for cid in customer_df["CUSTOMER_ID"]:
    result = ekyc.evaluate(cid)
    if result["status"]:
        if result["ekyc_risk"] == "HIGH":
            ekyc_high += 1
        elif result["ekyc_risk"] == "MEDIUM":
            ekyc_medium += 1
        else:
            ekyc_low += 1

d1, d2, d3 = st.columns(3)

d1.metric("High eKYC", ekyc_high)
d2.metric("Medium eKYC", ekyc_medium)
d3.metric("Low eKYC", ekyc_low)

# ======================================
# Screening Summary
# ======================================

st.divider()

st.subheader("🔍 Screening Summary")

screen_high = 0
screen_medium = 0
screen_low = 0

for cid in customer_df["CUSTOMER_ID"]:
    result = screen.evaluate_customer(cid)
    if result["status"]:
        if result["risk_level"] == "HIGH":
            screen_high += 1
        elif result["risk_level"] == "MEDIUM":
            screen_medium += 1
        else:
            screen_low += 1

e1, e2, e3 = st.columns(3)

e1.metric("High Screening", screen_high)
e2.metric("Medium Screening", screen_medium)
e3.metric("Low Screening", screen_low)

st.divider()
# ======================================
# Transaction Amount Chart
# ======================================

st.subheader("📈 Transaction Amount")

if txn_df.empty:
    st.info("No transaction data.")
else:
    fig = px.bar(
        txn_df,
        x="TXN_ID",
        y="AMOUNT",
        color="COUNTRY",
        title="Transaction Amount"
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ======================================
# Fraud Distribution
# ======================================

if "FRAUD_LABEL" in txn_df.columns:
    st.subheader("🚨 Fraud Distribution")

    fraud_chart = (
        txn_df["FRAUD_LABEL"]
        .value_counts()
        .reset_index()
    )

    fraud_chart.columns = ["Fraud", "Count"]
    fraud_chart["Fraud"] = fraud_chart["Fraud"].replace({
        0: "Normal",
        1: "Fraud"
    })

    fig = px.pie(
        fraud_chart,
        names="Fraud",
        values="Count",
        title="Fraud vs Normal"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ======================================
# Country Distribution
# ======================================

st.subheader("🌍 Transaction by Country")

country = (
    txn_df["COUNTRY"]
    .value_counts()
    .reset_index()
)

country.columns = ["Country", "Transactions"]

fig = px.bar(
    country,
    x="Country",
    y="Transactions",
    color="Transactions",
    title="Country Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ======================================
# Merchant Risk
# ======================================

st.subheader("🏪 Merchant Risk")

if merchant_df.empty:
    st.info("No merchant data.")
else:
    merchant_risk = (
        merchant_df["RISK_LEVEL"]
        .value_counts()
        .reset_index()
    )

    merchant_risk.columns = ["Risk", "Count"]

    fig = px.bar(
        merchant_risk,
        x="Risk",
        y="Count",
        color="Risk",
        title="Merchant Risk"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ======================================
# Alert Level
# ======================================

if not alert_df.empty:
    st.subheader("🚨 Alert Level")

    if "ALERT_LEVEL" in alert_df.columns:
        level = (
            alert_df["ALERT_LEVEL"]
            .value_counts()
            .reset_index()
        )

        level.columns = ["Level", "Count"]

        fig = px.bar(
            level,
            x="Level",
            y="Count",
            color="Level",
            title="Alert Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ======================================
# Case Status
# ======================================

if not case_df.empty:
    st.subheader("📂 Case Status")

    status = (
        case_df["STATUS"]
        .value_counts()
        .reset_index()
    )

    status.columns = ["Status", "Count"]

    fig = px.pie(
        status,
        names="Status",
        values="Count",
        title="Case Status"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ======================================
# Top Merchant
# ======================================

st.subheader("🏪 Top Merchant")

merchant_amount = (
    txn_df.groupby("MERCHANT_ID")["AMOUNT"]
    .sum()
    .reset_index()
)

merchant_amount = merchant_amount.sort_values(
    "AMOUNT",
    ascending=False
)

fig = px.bar(
    merchant_amount.head(10),
    x="MERCHANT_ID",
    y="AMOUNT",
    title="Top Merchant by Amount"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ======================================
# Top Customer
# ======================================

st.subheader("👤 Top Customer")

customer_amount = (
    txn_df.groupby("CUSTOMER_ID")["AMOUNT"]
    .sum()
    .reset_index()
)

customer_amount = customer_amount.sort_values(
    "AMOUNT",
    ascending=False
)

fig = px.bar(
    customer_amount.head(10),
    x="CUSTOMER_ID",
    y="AMOUNT",
    title="Top Customer by Amount"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()