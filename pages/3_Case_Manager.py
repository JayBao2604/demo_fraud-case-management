import streamlit as st
import pandas as pd
import plotly.express as px

from modules.loader import DatabaseLoader
from modules.case_manager import CaseManager

# =====================================
# Page Config
# =====================================

st.set_page_config(
    page_title="Case Manager",
    page_icon="📂",
    layout="wide"
)

# =====================================
# Cache Resource
# =====================================

@st.cache_resource
def get_loader():
    return DatabaseLoader()

@st.cache_resource
def get_case_manager():
    return CaseManager()

db = get_loader()
case_manager = get_case_manager()

# =====================================
# Load Data
# =====================================

@st.cache_data(ttl=10)
def load_cases():

    result = case_manager.get_cases()

    if isinstance(result, dict):

        if result.get("status"):

            return result["cases"]

        return pd.DataFrame()

    return result


cases = load_cases()

st.title("📂 Fraud Case Management")

if cases.empty:

    st.info("No investigation case found.")

    st.stop()

# =====================================
# Sidebar
# =====================================

st.sidebar.header("Filter")

status_filter = st.sidebar.multiselect(

    "Status",

    sorted(cases["STATUS"].dropna().unique()),

    default=sorted(cases["STATUS"].dropna().unique())

)

search_case = st.sidebar.text_input(

    "Search Case ID"

)

filtered = cases.copy()

if status_filter:

    filtered = filtered[
        filtered["STATUS"].isin(status_filter)
    ]

if search_case:

    filtered = filtered[
        filtered["CASE_ID"]
        .astype(str)
        .str.contains(search_case)
    ]

# =====================================
# KPI
# =====================================

st.subheader("📊 Investigation Summary")

open_case = len(
    filtered[
        filtered["STATUS"]=="OPEN"
    ]
)

progress_case = len(
    filtered[
        filtered["STATUS"]=="IN_PROGRESS"
    ]
)

closed_case = len(
    filtered[
        filtered["STATUS"]=="CLOSED"
    ]
)

total_case = len(filtered)

k1,k2,k3,k4 = st.columns(4)

k1.metric(
    "Total",
    total_case
)

k2.metric(
    "Open",
    open_case
)

k3.metric(
    "In Progress",
    progress_case
)

k4.metric(
    "Closed",
    closed_case
)

st.divider()

# =====================================
# Case Table
# =====================================

st.subheader("📋 Investigation Cases")

st.dataframe(

    filtered,

    use_container_width=True,

    height=350

)

st.divider()

# =====================================
# Select Case
# =====================================

case_id = st.selectbox(

    "Select Investigation Case",

    filtered["CASE_ID"]

)

selected = filtered[
    filtered["CASE_ID"]==case_id
].iloc[0]
# =====================================
# Case Detail
# =====================================

st.subheader("📄 Case Information")

left, right = st.columns(2)

with left:

    st.metric(
        "Case ID",
        selected["CASE_ID"]
    )

    st.metric(
        "Transaction ID",
        selected["TXN_ID"]
    )

    st.metric(
        "Risk Score",
        selected["RISK_SCORE"]
    )

with right:

    st.metric(
        "Status",
        selected["STATUS"]
    )

    st.metric(
        "Created Time",
        str(selected["CREATED_TIME"])
    )

st.divider()

# =====================================
# Transaction Detail
# =====================================

st.subheader("💳 Transaction Detail")

try:

    txn = db.get_transaction(
        selected["TXN_ID"]
    )

    if not txn.empty:

        txn = txn.iloc[0]

        c1, c2 = st.columns(2)

        with c1:

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

        with c2:

            st.metric(
                "Country",
                txn["COUNTRY"]
            )

            st.metric(
                "Device",
                txn["DEVICE_ID"]
            )

            st.metric(
                "Transaction Time",
                str(txn["TXN_TIME"])
            )

    else:

        st.info("Transaction not found.")

except Exception as e:

    st.error(e)

st.divider()

# =====================================
# Customer Detail
# =====================================

st.subheader("👤 Customer Information")

try:

    customer = db.get_customer(
        txn["CUSTOMER_ID"]
    )

    if not customer.empty:

        customer = customer.iloc[0]

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

        st.write(
            "**KYC Level:**",
            customer["KYC_LEVEL"]
        )

    else:

        st.info("Customer not found.")

except Exception:

    st.info("Customer information unavailable.")

st.divider()

# =====================================
# Account Information
# =====================================

st.subheader("🏦 Account Information")

try:

    account = db.get_account(
        txn["CUSTOMER_ID"]
    )

    if not account.empty:

        st.dataframe(

            account,

            use_container_width=True

        )

    else:

        st.info("No account found.")

except Exception:

    pass

st.divider()

# =====================================
# Terminal Information
# =====================================

st.subheader("🖥️ Terminal Information")

try:

    if "TERMINAL_ID" in txn.index:

        terminal = db.get_terminal(
            txn["TERMINAL_ID"]
        )

        if not terminal.empty:

            st.dataframe(

                terminal,

                use_container_width=True

            )

        else:

            st.info("Terminal not found.")

except Exception:

    pass

st.divider()

# =====================================
# Transaction History
# =====================================

st.subheader("📜 Customer Transaction History")

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
            "No transaction history."
        )

except Exception:

    pass

st.divider()
# =====================================
# Update Case
# =====================================

st.subheader("✏️ Update Investigation")

new_status = st.selectbox(
    "Case Status",
    [
        "OPEN",
        "IN_PROGRESS",
        "CLOSED"
    ],
    index=[
        "OPEN",
        "IN_PROGRESS",
        "CLOSED"
    ].index(selected["STATUS"])
    if selected["STATUS"] in ["OPEN", "IN_PROGRESS", "CLOSED"]
    else 0
)

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "💾 Update Status",
        use_container_width=True
    ):

        try:

            result = case_manager.update_status(
                case_id,
                new_status
            )

            if isinstance(result, dict):

                if result.get("status"):

                    st.success(result["message"])

                else:

                    st.error(result["message"])

            else:

                st.success("Case updated successfully.")

            st.rerun()

        except Exception as e:

            st.error(e)

with col2:

    if st.button(
        "✅ Close Case",
        use_container_width=True
    ):

        try:

            result = case_manager.close_case(
                case_id
            )

            if isinstance(result, dict):

                if result.get("status"):

                    st.success(result["message"])

                else:

                    st.error(result["message"])

            else:

                st.success("Case closed successfully.")

            st.rerun()

        except Exception as e:

            st.error(e)

st.divider()

# =====================================
# Delete Case
# =====================================

st.subheader("🗑️ Delete Case")

confirm_delete = st.checkbox(
    "I understand this action cannot be undone."
)

if st.button(
    "Delete Case",
    type="primary",
    use_container_width=True,
    disabled=not confirm_delete
):

    try:

        result = case_manager.delete_case(
            case_id
        )

        if isinstance(result, dict):

            if result.get("status"):

                st.success(result["message"])

            else:

                st.error(result["message"])

        else:

            st.success("Case deleted successfully.")

        st.rerun()

    except Exception as e:

        st.error(e)

st.divider()

# =====================================
# Status Distribution
# =====================================

st.subheader("📊 Case Status Distribution")

status_chart = (
    filtered["STATUS"]
    .value_counts()
    .reset_index()
)

status_chart.columns = [
    "Status",
    "Count"
]

st.bar_chart(
    status_chart.set_index("Status")
)

# =====================================
# Risk Score Distribution
# =====================================

if "RISK_SCORE" in filtered.columns:

    st.subheader("📈 Risk Score Distribution")

    st.bar_chart(
        filtered.set_index("CASE_ID")["RISK_SCORE"]
    )

st.divider()

# =====================================
# Recent Cases
# =====================================

st.subheader("🕒 Recent Investigation Cases")

recent = filtered.sort_values(
    "CREATED_TIME",
    ascending=False
)

st.dataframe(

    recent.head(10),

    use_container_width=True,

    height=300

)

st.divider()