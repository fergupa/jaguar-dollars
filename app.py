"""Gator Dollars - School Reward System.

A Streamlit app for managing a school reward currency system.
"""

import streamlit as st
from database import init_db, is_db_empty
from seed_data import seed
from auth import authenticate, logout
import models


# ── Page Config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gator Dollars",
    page_icon="🐊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        font-family: 'Segoe UI', sans-serif;
    }
    div[data-testid="stMetric"] {
        background-color: #e8f5e9;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #2e7d32;
    }
    .big-balance {
        font-size: 3rem;
        font-weight: bold;
        color: #2e7d32;
        text-align: center;
        padding: 20px;
    }
    .gator-header {
        color: #2e7d32;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Initialize Database ───────────────────────────────────────────────
init_db()
if is_db_empty():
    seed()

# ── Authentication ─────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 class='gator-header'>🐊 Gator Dollars</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Your school reward system</p>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("---")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", use_container_width=True)

            if submitted:
                if username and password:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.warning("Please enter both username and password.")

        st.markdown("---")
        with st.expander("Demo Credentials"):
            st.markdown("""
            **Teachers:**
            - `mrivera` / `gator123` (Mrs. Rivera - Science)
            - `mthompson` / `gator123` (Mr. Thompson - English)
            - `mchen` / `gator123` (Ms. Chen - Math)

            **Students:**
            - `jsmith` / `student` (Jordan Smith)
            - `agarcia` / `student` (Alex Garcia)
            - `kpatel` / `student` (Kira Patel)
            - All students use password: `student`
            """)

else:
    user = st.session_state.user

    # ── Sidebar ────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"### 🐊 Gator Dollars")
        st.markdown(f"**{user['display_name']}**")

        if user["role"] == "teacher":
            st.caption("Teacher Account")
            bank = models.get_bank_balance(user["id"])
            st.metric("Bank Balance", f"${bank}")
        else:
            st.caption("Student Account")
            balance = models.get_balance(user["id"])
            st.metric("My Balance", f"${balance}")

        st.markdown("---")
        if st.button("Log Out", use_container_width=True):
            logout()
            st.rerun()

    # ── Navigation ─────────────────────────────────────────────────────
    if user["role"] == "teacher":
        pages = [
            st.Page("pages/teacher_dashboard.py", title="Dashboard", icon="📊"),
            st.Page("pages/give_dollars.py", title="Give Dollars", icon="💰"),
            st.Page("pages/manage_prizes.py", title="Manage Prizes", icon="🎁"),
            st.Page("pages/approve_nominations.py", title="Nominations", icon="⭐"),
            st.Page("pages/manage_pool.py", title="Class Pools", icon="🏊"),
            st.Page("pages/transaction_history.py", title="History", icon="📋"),
        ]
    else:
        pages = [
            st.Page("pages/student_dashboard.py", title="My Gator Dollars", icon="🐊"),
            st.Page("pages/redeem_prizes.py", title="Prize Store", icon="🎁"),
            st.Page("pages/nominate_peer.py", title="Nominate", icon="⭐"),
            st.Page("pages/class_pool.py", title="Class Pool", icon="🏊"),
            st.Page("pages/transaction_history.py", title="History", icon="📋"),
        ]

    nav = st.navigation(pages)
    nav.run()
