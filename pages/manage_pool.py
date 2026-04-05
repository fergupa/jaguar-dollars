"""Manage Pool - view and manage classroom pool balances."""

import streamlit as st
from auth import require_role
import models

require_role("teacher")
user = st.session_state.user

st.title("🏊 Class Pools")

classrooms = models.get_teacher_classrooms(user["id"])

if not classrooms:
    st.warning("No classrooms assigned to you.")
    st.stop()

for classroom in classrooms:
    cls = models.get_classroom(classroom["id"])
    st.subheader(f"{cls['name']}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Pool Balance", f"${cls['pool_balance']}")
    with col2:
        # Show next achievable class prize
        class_prizes = models.list_prizes(prize_type="classroom")
        if class_prizes:
            affordable = [p for p in class_prizes if p["cost"] <= cls["pool_balance"]]
            next_prize = [p for p in class_prizes if p["cost"] > cls["pool_balance"]]
            if next_prize:
                progress = cls["pool_balance"] / next_prize[0]["cost"]
                st.write(f"Next prize: {next_prize[0]['emoji']} {next_prize[0]['name']} (${next_prize[0]['cost']})")
                st.progress(min(progress, 1.0))

    # Contribution leaderboard
    contributions = models.get_pool_contributions(classroom["id"])
    if contributions:
        st.write("**Top Contributors:**")
        for i, c in enumerate(contributions[:5], 1):
            st.write(f"{i}. {c['display_name']} - ${c['total_contributed']}")

    # Redeem class prize
    class_prizes = models.list_prizes(prize_type="classroom")
    affordable = [p for p in class_prizes if p["cost"] <= cls["pool_balance"]]

    if affordable:
        st.write("**Available Class Prizes:**")
        for prize in affordable:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{prize['emoji']} **{prize['name']}** - ${prize['cost']}")
                st.caption(prize["description"])
            with col2:
                if st.button("Redeem", key=f"pool_redeem_{classroom['id']}_{prize['id']}",
                             use_container_width=True):
                    success, msg = models.redeem_class_prize(classroom["id"], prize["id"], user["id"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.markdown("---")
