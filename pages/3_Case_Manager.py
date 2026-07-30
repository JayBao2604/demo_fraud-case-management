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
    return case_manager.get_cases()

cases = load_cases()

# Đảm bảo cases là DataFrame
if not isinstance(cases, pd.DataFrame):
    cases = pd.DataFrame(cases)

st.title("📂 Fraud Case Management")

if cases.empty:
    st.info("💡 Hiện tại chưa có ca điều tra (Case) nào. Vui lòng tạo Case từ các giao dịch nghi ngờ để bắt đầu theo dõi.")
    # Đã bỏ st.stop() để giao diện phía dưới vẫn hiển thị bình thường

# =====================================
# Sidebar
# =====================================

st.sidebar.header("Filter")

filtered = cases.copy()

if not cases.empty and "STATUS" in cases.columns:
    status_filter = st.sidebar.multiselect(
        "Status",
        sorted(cases["STATUS"].dropna().unique()),
        default=sorted(cases["STATUS"].dropna().unique())
    )
    if status_filter:
        filtered = filtered[filtered["STATUS"].isin(status_filter)]

if not cases.empty and "CASE_ID" in cases.columns:
    search_case = st.sidebar.text_input("Search Case ID")
    if search_case:
        filtered = filtered[filtered["CASE_ID"].astype(str).str.contains(search_case)]

# =====================================
# KPI
# =====================================

st.subheader("📊 Investigation Summary")

open_case = len(filtered[filtered["STATUS"]=="OPEN"]) if not filtered.empty and "STATUS" in filtered.columns else 0
progress_case = len(filtered[filtered["STATUS"]=="IN_PROGRESS"]) if not filtered.empty and "STATUS" in filtered.columns else 0
closed_case = len(filtered[filtered["STATUS"]=="CLOSED"]) if not filtered.empty and "STATUS" in filtered.columns else 0
total_case = len(filtered)

k1,k2,k3,k4 = st.columns(4)
k1.metric("Total", total_case)
k2.metric("Open", open_case)
k3.metric("In Progress", progress_case)
k4.metric("Closed", closed_case)

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
# Select Case & Details (Chỉ hiện khi có dữ liệu)
# =====================================

if not filtered.empty and "CASE_ID" in filtered.columns:

    case_id = st.selectbox(
        "Select Investigation Case",
        filtered["CASE_ID"]
    )

    selected = filtered[filtered["CASE_ID"]==case_id].iloc[0]

    # =====================================
    # Case Detail
    # =====================================
    st.subheader("📄 Case Information")

    left, right = st.columns(2)

    with left:
        st.metric("Case ID", selected.get("CASE_ID", "N/A"))
        st.metric("Transaction ID", selected.get("TXN_ID", "N/A"))
        
        # Sửa lỗi xung đột RISK_SCORE và PRIORITY
        risk_display = selected.get("RISK_SCORE", selected.get("PRIORITY", "N/A"))
        st.metric("Risk Score / Priority", risk_display)

    with right:
        st.metric("Status", selected.get("STATUS", "N/A"))
        st.metric("Created Time", str(selected.get("CREATED_TIME", "N/A")))

    st.divider()

    # =====================================
    # Transaction Detail
    # =====================================
    st.subheader("💳 Transaction Detail")
    try:
        txn = db.get_transaction(selected["TXN_ID"])
        if not txn.empty:
            txn = txn.iloc[0]
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Customer", txn.get("CUSTOMER_ID", "N/A"))
                st.metric("Merchant", txn.get("MERCHANT_ID", "N/A"))
                amount = txn.get('AMOUNT', 0)
                st.metric("Amount", f"{amount:,.0f}" if pd.notnull(amount) else "N/A")
            with c2:
                st.metric("Country", txn.get("COUNTRY", "N/A"))
                st.metric("Device", txn.get("DEVICE_ID", "N/A"))
                st.metric("Transaction Time", str(txn.get("TXN_TIME", "N/A")))
        else:
            st.info("Transaction not found.")
    except Exception as e:
        st.error(f"Error loading transaction: {e}")

    st.divider()

    # =====================================
    # Customer Detail
    # =====================================
    st.subheader("👤 Customer Information")
    try:
        customer = db.get_customer(txn["CUSTOMER_ID"])
        if not customer.empty:
            customer = customer.iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.metric("Customer Name", customer.get("FULL_NAME", "N/A"))
            c2.metric("Risk Rating", customer.get("RISK_RATING", "N/A"))
            c3.metric("AML Score", customer.get("AML_SCORE", "N/A"))
            st.write("**KYC Level:**", customer.get("KYC_LEVEL", "N/A"))
        else:
            st.info("Customer not found.")
    except Exception:
        st.info("Customer information unavailable.")

    st.divider()

    # =====================================
    # Update / Delete Actions
    # =====================================
    st.subheader("✏️ Manage Case")
    
    current_status = selected.get("STATUS", "OPEN")
    status_options = ["OPEN", "IN_PROGRESS", "CLOSED"]
    
    new_status = st.selectbox(
        "Case Status",
        status_options,
        index=status_options.index(current_status) if current_status in status_options else 0
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Update Status", use_container_width=True):
            try:
                result = case_manager.update_status(case_id, new_status)
                st.success("Case updated successfully.")
                st.rerun()
            except Exception as e:
                st.error(e)

    with col2:
        if st.button("✅ Close Case", use_container_width=True):
            try:
                result = case_manager.close_case(case_id)
                st.success("Case closed successfully.")
                st.rerun()
            except Exception as e:
                st.error(e)