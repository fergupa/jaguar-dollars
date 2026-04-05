"""Give Dollars - award Gator Dollars to students."""

import streamlit as st
import pandas as pd
from auth import require_role
import models

require_role("teacher")
user = st.session_state.user

st.title("💰 Give Gator Dollars")

bank = models.get_bank_info(user["id"])
st.info(f"Your bank balance: **${bank['balance']}**" if bank else "Bank not set up.")

# ── Classroom Filter ───────────────────────────────────────────────────
classrooms = models.get_teacher_classrooms(user["id"])
if not classrooms:
    st.warning("No classrooms assigned to you.")
    st.stop()

classroom_names = {c["name"]: c["id"] for c in classrooms}
selected_classroom = st.selectbox("Select Classroom", options=list(classroom_names.keys()))
classroom_id = classroom_names[selected_classroom]

# ── Student List ───────────────────────────────────────────────────────
students = models.get_students_by_classroom(classroom_id)

if not students:
    st.info("No students in this classroom.")
    st.stop()

st.subheader("Students")

# Show current balances
df = pd.DataFrame([{"Name": s["display_name"], "Balance": f"${s['balance']}"} for s in students])
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")

# ── Individual Award ───────────────────────────────────────────────────
st.subheader("Award to Individual Student")
with st.form("individual_award", clear_on_submit=True):
    student_options = {s["display_name"]: s["id"] for s in students}
    selected = st.selectbox("Student", options=list(student_options.keys()))
    amount = st.slider("Amount", 1, 50, 5)
    note = st.text_input("Reason", placeholder="What did they do well?")

    if st.form_submit_button("Award", use_container_width=True):
        if note.strip():
            if models.award_dollars(user["id"], student_options[selected], amount, note):
                st.success(f"Awarded ${amount} to {selected}!")
                st.rerun()
            else:
                st.error("Not enough dollars in your bank!")
        else:
            st.warning("Please provide a reason.")

st.markdown("---")

# ── Batch Award ────────────────────────────────────────────────────────
st.subheader("Award to Multiple Students")
with st.form("batch_award", clear_on_submit=True):
    selected_students = st.multiselect(
        "Select Students",
        options=[s["display_name"] for s in students],
    )
    batch_amount = st.slider("Amount (each)", 1, 25, 5, key="batch_amount")
    batch_note = st.text_input("Reason", placeholder="What did they do well?", key="batch_note")

    if st.form_submit_button("Award to All Selected", use_container_width=True):
        if not selected_students:
            st.warning("Please select at least one student.")
        elif not batch_note.strip():
            st.warning("Please provide a reason.")
        else:
            name_to_id = {s["display_name"]: s["id"] for s in students}
            success_count = 0
            for name in selected_students:
                if models.award_dollars(user["id"], name_to_id[name], batch_amount, batch_note):
                    success_count += 1
            if success_count == len(selected_students):
                st.success(f"Awarded ${batch_amount} each to {success_count} students!")
            elif success_count > 0:
                st.warning(f"Awarded to {success_count}/{len(selected_students)} students. Bank may be running low.")
            else:
                st.error("Not enough dollars in your bank!")
            st.rerun()
