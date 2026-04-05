"""Nominate a Peer - students can nominate classmates for Gator Dollars."""

import streamlit as st
from auth import require_role
import models

require_role("student")
user = st.session_state.user

st.title("⭐ Nominate a Classmate")

st.write("Know someone who's been awesome? Nominate them to earn Gator Dollars! "
         "Your teacher will review the nomination.")

# ── Nomination Form ────────────────────────────────────────────────────
classmates = models.get_students_by_classroom(user["classroom_id"])
# Remove self from list
classmates = [s for s in classmates if s["id"] != user["id"]]

if not classmates:
    st.info("No other students in your classroom.")
    st.stop()

with st.form("nominate_form", clear_on_submit=True):
    classmate_options = {s["display_name"]: s["id"] for s in classmates}
    selected_name = st.selectbox("Who deserves recognition?", options=list(classmate_options.keys()))
    reason = st.text_area("Why are you nominating them?",
                          placeholder="Tell us what they did! (at least 20 characters)",
                          max_chars=300)
    suggested_amount = st.slider("How many Gator Dollars do you suggest?", 1, 10, 5)

    if st.form_submit_button("Submit Nomination", use_container_width=True):
        if len(reason.strip()) < 20:
            st.warning("Please write at least 20 characters explaining why you're nominating them.")
        else:
            models.create_nomination(
                user["id"],
                classmate_options[selected_name],
                reason.strip(),
                suggested_amount,
            )
            st.success(f"Nomination submitted for {selected_name}! Your teacher will review it.")
            st.rerun()

st.markdown("---")

# ── My Nominations ────────────────────────────────────────────────────
st.subheader("My Nominations")

nominations = models.get_nominations_by_user(user["id"])
if nominations:
    for nom in nominations:
        status_icon = {"pending": "🕐", "approved": "✅", "denied": "❌"}.get(nom["status"], "❓")
        with st.container(border=True):
            st.write(f"{status_icon} **{nom['nominee_name']}** - {nom['status'].upper()}")
            st.caption(f"Reason: {nom['reason']}")
            st.caption(f"Suggested: ${nom['suggested_amount']}")
else:
    st.info("You haven't made any nominations yet.")
