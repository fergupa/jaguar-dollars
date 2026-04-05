"""Class Pool - students can contribute to their classroom's pool."""

import streamlit as st
from auth import require_role
import models

require_role("student")
user = st.session_state.user

st.title("🏊 Class Pool")

classroom = models.get_classroom(user["classroom_id"])
if not classroom:
    st.error("Classroom not found.")
    st.stop()

balance = models.get_balance(user["id"])

st.write(f"**{classroom['name']}** - Pool together with your classmates for awesome class prizes!")

# ── Pool Balance & Progress ────────────────────────────────────────────
st.metric("Class Pool Balance", f"${classroom['pool_balance']}")

class_prizes = models.list_prizes(prize_type="classroom")
if class_prizes:
    st.subheader("Class Prizes We Can Earn")
    for prize in class_prizes:
        progress = min(classroom["pool_balance"] / prize["cost"], 1.0)
        remaining = max(prize["cost"] - classroom["pool_balance"], 0)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"{prize['emoji']} **{prize['name']}** - ${prize['cost']}")
            st.caption(prize["description"])
            st.progress(progress)
        with col2:
            if remaining > 0:
                st.caption(f"${remaining} to go")
            else:
                st.success("Ready!")

st.markdown("---")

# ── Contribute ─────────────────────────────────────────────────────────
st.subheader("Contribute to the Pool")
st.info(f"Your balance: **${balance}**")

if balance > 0:
    with st.form("contribute_form"):
        amount = st.slider("How much to contribute?", 1, min(balance, 50), min(5, balance))
        if st.form_submit_button("Contribute", use_container_width=True):
            success, msg = models.contribute_to_pool(user["id"], user["classroom_id"], amount)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
else:
    st.caption("Earn some Gator Dollars first to contribute!")

st.markdown("---")

# ── Contribution Leaderboard ───────────────────────────────────────────
st.subheader("Top Contributors")
contributions = models.get_pool_contributions(user["classroom_id"])
if contributions:
    for i, c in enumerate(contributions, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        st.write(f"{medal} **{c['display_name']}** - ${c['total_contributed']}")
else:
    st.info("No contributions yet. Be the first!")
