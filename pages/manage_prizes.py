"""Manage Prizes - add, edit, and toggle prizes."""

import streamlit as st
from auth import require_role
import models

require_role("teacher")

st.title("🎁 Manage Prizes")

# ── Tabs ───────────────────────────────────────────────────────────────
tab_individual, tab_classroom, tab_add = st.tabs(["Individual Prizes", "Classroom Prizes", "Add New Prize"])

with tab_individual:
    prizes = models.list_prizes(prize_type="individual", active_only=False)
    if prizes:
        for prize in prizes:
            status = "Active" if prize["active"] else "Inactive"
            qty = "Unlimited" if prize["quantity"] == -1 else f"{prize['quantity']} left"
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"{prize['emoji']} **{prize['name']}** - {prize['description']}")
            with col2:
                st.write(f"${prize['cost']}")
            with col3:
                st.write(qty)
            with col4:
                if st.button(
                    "Deactivate" if prize["active"] else "Activate",
                    key=f"toggle_ind_{prize['id']}",
                ):
                    models.toggle_prize(prize["id"])
                    st.rerun()
    else:
        st.info("No individual prizes yet.")

with tab_classroom:
    prizes = models.list_prizes(prize_type="classroom", active_only=False)
    if prizes:
        for prize in prizes:
            status = "Active" if prize["active"] else "Inactive"
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"{prize['emoji']} **{prize['name']}** - {prize['description']}")
            with col2:
                st.write(f"${prize['cost']}")
            with col3:
                st.caption(status)
            with col4:
                if st.button(
                    "Deactivate" if prize["active"] else "Activate",
                    key=f"toggle_cls_{prize['id']}",
                ):
                    models.toggle_prize(prize["id"])
                    st.rerun()
    else:
        st.info("No classroom prizes yet.")

with tab_add:
    with st.form("add_prize", clear_on_submit=True):
        st.subheader("Create New Prize")
        name = st.text_input("Prize Name", placeholder="e.g., Homework Pass")
        description = st.text_input("Description", placeholder="What does the student get?")
        cost = st.number_input("Cost (Gator Dollars)", min_value=1, max_value=500, value=10)
        prize_type = st.radio("Prize Type", ["individual", "classroom"], horizontal=True)
        emoji = st.text_input("Emoji", value="🎁", max_chars=2)

        has_limit = st.checkbox("Limited quantity?")
        quantity = -1
        if has_limit:
            quantity = st.number_input("How many available?", min_value=1, value=10)

        if st.form_submit_button("Create Prize", use_container_width=True):
            if name.strip() and description.strip():
                models.create_prize(name, description, cost, prize_type, quantity, emoji)
                st.success(f"Prize '{name}' created!")
                st.rerun()
            else:
                st.warning("Please fill in the name and description.")
