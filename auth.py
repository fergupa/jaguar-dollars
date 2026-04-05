"""Authentication helpers for Gator Dollars.

Uses SHA-256 for password hashing (demo-grade only).
In production, use bcrypt or argon2.
"""

import hashlib
import streamlit as st
from database import get_connection


def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()


def authenticate(username: str, password: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, password_hash, display_name, role, classroom_id "
        "FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()

    if row and row["password_hash"] == hash_password(password):
        return {
            "id": row["id"],
            "username": row["username"],
            "display_name": row["display_name"],
            "role": row["role"],
            "classroom_id": row["classroom_id"],
        }
    return None


def require_role(role: str):
    user = st.session_state.get("user")
    if not user or user["role"] != role:
        st.error("You don't have permission to view this page.")
        st.stop()


def logout():
    for key in ["user", "authenticated"]:
        st.session_state.pop(key, None)
