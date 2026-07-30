import streamlit as st
import sqlite3
import pandas as pd
import time
from modules.alert_engine import AlertEngine

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Fraud Lifecycle Management",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

.main{
    padding-top:2rem;
}

.big-title{
    font-size:42px;
    font-weight:700;
    color:#1f77b4;
}

.sub-title{
    font-size:20px;
    color:gray;
}

.card{
        background-color:#F8F9FA;
    padding:25px;
    border-radius:12px;
    border:1px solid #DDDDDD;
    text-align:center;
}

.card h3{
    color:#1f77b4;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    """
<div class="big-title">
🛡️ Fraud Lifecycle Management
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="sub-title">
Banking Fraud Detection & Investigation Platform
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# ==========================================================
# WELCOME
# ==========================================================

st.markdown("## Welcome")

st.write("""
This project simulates an end-to-end Banking Fraud Lifecycle Management System.

Please choose a module from the left sidebar to continue.
""")

st.divider()

# ==========================================================
# MODULES
# ==========================================================

st.subheader("Available Modules")

col1, col2 = st.columns(2)

with col1:

    st.info("📊 Dashboard")

    st.write("System Overview")
    st.write("Fraud Statistics")
    st.write("KPI Monitoring")

    st.info("📡 Live Transaction")

    st.write("Transaction Monitoring")
    st.write("Real-time Detection")
    st.write("Risk Analysis")

    st.info("📂 Case Manager")

    st.write("Case Investigation")
    st.write("Case Status")
    st.write("Evidence")

with col2:

    st.info("⚙ Rule Manager")

    st.write("Fraud Rules")
    st.write("Threshold")
    st.write("Risk Score")

    st.info("📈 Report")

    st.write("Alert Report")
    st.write("Fraud Report")
    st.write("Management Report")

st.divider()

# ==========================================================
# START
# ==========================================================

st.success("✅ Database Connected")

st.info("👈 Select a page from the sidebar to start using the system.")

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

st.caption("Fraud Lifecycle Management System")
st.caption("Version 2.0")
st.caption("Powered by Streamlit + SQLite")