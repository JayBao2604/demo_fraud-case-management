import streamlit as st
from modules.auth_manager import AuthManager

# ==========================================
# PAGE CONFIG & SESSION INIT
# ==========================================
st.set_page_config(page_title="Fraud Case Management Portal", page_icon="🔒", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = None
    st.session_state.role = None

auth = AuthManager()

# ==========================================
# LOGIN PAGE (GOOGLE SSO SIMULATION)
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🔐 FRAUD CASE MANAGEMENT PORTAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Single Sign-On (SSO) Authentication</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # Giao diện nút Google Login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <img src="https://developers.google.com/identity/images/btn_google_signin_dark_normal_web.png" width="200">
            </div>
            """, unsafe_allow_html=True
        )
        
        # Mô phỏng quá trình Google trả về Email (Trong thực tế, bạn sẽ dùng Google OAuth component ở đây)
        with st.form("mock_google_login"):
            st.caption("Mô phỏng Email được Google trả về sau khi click nút bên trên:")
            email_input = st.text_input("Google Email", "admin@bank.com")
            submitted = st.form_submit_button("Tiếp tục (Simulate OAuth)", use_container_width=True)

            if submitted:
                res = auth.authenticate_by_email(email_input)
                if res["status"]:
                    st.session_state.logged_in = True
                    st.session_state.email = email_input
                    st.session_state.role = res["role"]
                    st.rerun()
                else:
                    st.error(res["message"])

# ==========================================
# MAIN PORTAL (AFTER LOGIN)
# ==========================================
else:
    st.sidebar.success(f"👤 Welcome, **{st.session_state.email}**")
    st.sidebar.info(f"🔑 Role: **{st.session_state.role}**")
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.email = None
        st.session_state.role = None
        st.rerun()

    st.title("🛡️ Fraud Case Management Portal")
    st.success("Login successful! Please select a module from the left sidebar to continue.")

    # ==========================================
    # IAM/PAM MODULE (SYSTEM ADMIN ONLY)
    # ==========================================
    if st.session_state.role == "SYSTEM ADMIN":
        st.divider()
        st.subheader("👥 Identity & Access Management (IAM / PAM)")
        
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("**Create New User**")
            with st.form("create_user_form"):
                new_email = st.text_input("Google Workspace Email")
                new_role = st.selectbox("Role", ["USER", "FRAUD", "KSV", "SYSTEM ADMIN"])
                new_tele_id = st.text_input("Telegram Chat ID (Cho role FRAUD)", help="Để trống nếu không cần nhận notify")
                
                if st.form_submit_button("Grant Access", use_container_width=True):
                    if new_email:
                        res = auth.create_user(new_email, new_role, new_tele_id)
                        if res["status"]:
                            st.success(res["message"])
                        else:
                            st.error(res["message"])
                    else:
                        st.warning("Vui lòng nhập Email.")
        with c2:
            st.markdown("**User List**")
            st.dataframe(auth.get_all_users(), use_container_width=True)