"""Teacher Dashboard - overview stats and quick actions."""

import streamlit as st
from auth import require_role
import models

require_role("teacher")
user = st.session_state.user

st.title("📊 Teacher Dashboard")

# ── Summary Stats ──────────────────────────────────────────────────────
bank = models.get_bank_info(user["id"])
classrooms = models.get_teacher_classrooms(user["id"])
pending = models.get_pending_nominations()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Bank Balance", f"${bank['balance']}" if bank else "$0")
with col2:
    st.metric("Total Issued", f"${bank['total_issued']}" if bank else "$0")
with col3:
    student_count = sum(len(models.get_students_by_classroom(c["id"])) for c in classrooms)
    st.metric("My Students", student_count)
with col4:
    st.metric("Pending Nominations", len(pending))

st.markdown("---")

# ── Quick Award ────────────────────────────────────────────────────────
st.subheader("Quick Award")

all_students = []
for c in classrooms:
    students = models.get_students_by_classroom(c["id"])
    all_students.extend(students)

if all_students:
    with st.form("quick_award", clear_on_submit=True):
        student_options = {s["display_name"]: s["id"] for s in all_students}
        selected_name = st.selectbox("Select Student", options=list(student_options.keys()))
        amount = st.slider("Amount", min_value=1, max_value=25, value=5)
        note = st.text_input("Reason", placeholder="e.g., Great participation in class today!")

        if st.form_submit_button("Award Gator Dollars", use_container_width=True):
            if note.strip():
                success = models.award_dollars(user["id"], student_options[selected_name], amount, note)
                if success:
                    st.success(f"Awarded ${amount} to {selected_name}!")
                    st.rerun()
                else:
                    st.error("Not enough dollars in your bank!")
            else:
                st.warning("Please provide a reason for the award.")

st.markdown("---")

# ── Recent Activity ────────────────────────────────────────────────────
st.subheader("Recent Activity")

classroom_ids = [c["id"] for c in classrooms]
all_txns = []
for cid in classroom_ids:
    all_txns.extend(models.get_transactions(classroom_id=cid, limit=10))

# Sort and limit
all_txns.sort(key=lambda t: t["created_at"], reverse=True)
all_txns = all_txns[:10]

if all_txns:
    for txn in all_txns:
        icon = {"award": "💰", "redemption": "🎁", "pool_contrib": "🏊",
                "pool_redemption": "🎉", "nomination_award": "⭐"}.get(txn["type"], "📋")
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.write(icon)
        with col2:
            if txn["type"] == "award":
                st.write(f"**{txn['from_name']}** awarded **${txn['amount']}** to **{txn['to_name']}**")
            elif txn["type"] == "redemption":
                st.write(f"**{txn['from_name']}** {txn['note']}")
            elif txn["type"] == "pool_contrib":
                st.write(f"**{txn['from_name']}** contributed **${txn['amount']}** to class pool")
            elif txn["type"] == "nomination_award":
                st.write(f"**{txn['to_name']}** received **${txn['amount']}** from nomination")
            else:
                st.write(f"{txn['note']} - ${txn['amount']}")
        with col3:
            st.caption(txn["created_at"][:10] if txn["created_at"] else "")
else:
    st.info("No recent activity yet.")
