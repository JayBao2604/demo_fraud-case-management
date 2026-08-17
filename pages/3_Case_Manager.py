import streamlit as st
import pandas as pd
import plotly.express as px

from modules.loader import DatabaseLoader
from modules.case_manager import CaseManager
from modules.notifier import Notifier

# Khởi tạo Notifier
notifier = Notifier()

# =====================================
# Page Config
# =====================================

st.set_page_config(
    page_title="Case Manager",
    page_icon="📂",
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

# Chỉ cho phép FRAUD và KSV truy cập trang này
require_role(["FRAUD", "KSV"])

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
# Select Case & Details
# =====================================

if not filtered.empty and "CASE_ID" in filtered.columns:

    case_id = st.selectbox(
        "Select Investigation Case",
        filtered["CASE_ID"]
    )

    selected = filtered[filtered["CASE_ID"]==case_id].iloc[0]

    # Quy đổi RISK_SCORE hiện tại ra Severity Level để hiển thị
    current_score = int(selected.get("RISK_SCORE", 0))
    if current_score >= 80:
        current_sev = "CRITICAL"
    elif current_score >= 60:
        current_sev = "HIGH"
    elif current_score >= 40:
        current_sev = "MEDIUM"
    else:
        current_sev = "LOW"

    # =====================================
    # Case Detail
    # =====================================
    st.subheader("📄 Case Information")

    left, right = st.columns(2)

    with left:
        st.metric("Case ID", selected.get("CASE_ID", "N/A"))
        st.metric("Transaction ID", selected.get("TXN_ID", "N/A"))
        st.metric("Risk Score (Severity)", f"{current_score} ({current_sev})")

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
    # Update / Delete Actions (BẢO VỆ NÚT BẤM)
    # =====================================
    st.subheader("✏️ Manage Case")
    
    current_status = selected.get("STATUS", "OPEN")
    status_options = ["OPEN", "IN_PROGRESS", "CLOSED"]
    sev_options = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    c1, c2 = st.columns(2)
    with c1:
        new_status = st.selectbox(
            "Case Status",
            status_options,
            index=status_options.index(current_status) if current_status in status_options else 0
        )
    with c2:
        new_sev = st.selectbox(
            "Severity (Risk Level)",
            sev_options,
            index=sev_options.index(current_sev) if current_sev in sev_options else 0
        )

    col1, col2 = st.columns(2)
    
    # ----------------------------------------------------
    # QUYỀN UPDATE STATUS & SEVERITY: Chỉ dành cho KSV
    # ----------------------------------------------------
    with col1:
        if st.session_state.role == "KSV":
            if st.button("💾 Update Case", use_container_width=True):
                try:
                    # 1. Update Status
                    case_manager.update_status(case_id, new_status)
                    
                    # 2. Update Severity (Quy đổi ngược thành RISK_SCORE)
                    score_mapping = {"LOW": 20, "MEDIUM": 50, "HIGH": 70, "CRITICAL": 90}
                    new_score = score_mapping[new_sev]
                    case_manager.update_severity(case_id, new_score)

                    st.success("Case updated successfully.")
                    
                    # ---- KÍCH HOẠT THÔNG BÁO TELEGRAM (GỘP CẢ 2 THAY ĐỔI) ----
                    if current_status != new_status or current_sev != new_sev:
                        old_display = f"{current_status} ({current_sev})"
                        new_display = f"{new_status} ({new_sev})"
                        
                        notify_res = notifier.notify_fraud_team(
                            case_id=case_id, 
                            old_status=old_display, 
                            new_status=new_display, 
                            updater_email=st.session_state.email
                        )
                        if notify_res["status"]:
                            st.toast("Đã gửi cảnh báo Telegram cho team FRAUD!", icon="📲")
                    # ------------------------------------------------------------
                    
                    st.rerun()
                except Exception as e:
                    st.error(e)
        else:
            st.button("💾 Update Case", disabled=True, use_container_width=True)
            st.caption("🔒 Chỉ Kiểm Soát Viên (KSV) mới có quyền cập nhật Case.")

    # ----------------------------------------------------
    # QUYỀN CLOSE CASE: Chỉ dành cho FRAUD
    # ----------------------------------------------------
    with col2:
        if st.session_state.role == "FRAUD":
            if st.button("✅ Close Case", use_container_width=True):
                try:
                    case_manager.close_case(case_id)
                    st.success("Case closed successfully.")
                    st.rerun()
                except Exception as e:
                    st.error(e)
        else:
            st.button("✅ Close Case", disabled=True, use_container_width=True)
            st.caption("🔒 Chỉ FRAUD mới có quyền đóng Case.")