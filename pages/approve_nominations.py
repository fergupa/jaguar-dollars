"""Approve Nominations - review student peer nominations."""

import streamlit as st
from auth import require_role
import models

require_role("teacher")
user = st.session_state.user

st.title("⭐ Student Nominations")

tab_pending, tab_history = st.tabs(["Pending", "History"])

with tab_pending:
    classrooms = models.get_teacher_classrooms(user["id"])
    classroom_ids = [c["id"] for c in classrooms]

    all_pending = []
    for cid in classroom_ids:
        all_pending.extend(models.get_pending_nominations(classroom_id=cid))

    if not all_pending:
        st.info("No pending nominations to review.")
    else:
        st.write(f"**{len(all_pending)} nomination(s) awaiting review**")
        st.markdown("---")

        for nom in all_pending:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{nom['nominator_name']}** nominated **{nom['nominee_name']}**")
                    st.write(f"*\"{nom['reason']}\"*")
                    st.caption(f"Suggested amount: ${nom['suggested_amount']}")
                with col2:
                    adjusted_amount = st.number_input(
                        "Amount",
                        min_value=1, max_value=25,
                        value=nom["suggested_amount"],
                        key=f"amt_{nom['id']}",
                    )

                col_approve, col_deny = st.columns(2)
                with col_approve:
                    if st.button("Approve", key=f"approve_{nom['id']}", use_container_width=True):
                        if models.review_nomination(nom["id"], user["id"], "approved",
                                                    amount=adjusted_amount):
                            st.success(f"Approved! {nom['nominee_name']} receives ${adjusted_amount}.")
                            st.rerun()
                        else:
                            st.error("Could not approve. Check your bank balance.")
                with col_deny:
                    if st.button("Deny", key=f"deny_{nom['id']}", use_container_width=True):
                        models.review_nomination(nom["id"], user["id"], "denied",
                                                 review_note="Declined by teacher")
                        st.info("Nomination denied.")
                        st.rerun()

                st.markdown("---")

with tab_history:
    # Show all reviewed nominations for teacher's classrooms
    from database import get_connection
    conn = get_connection()
    classrooms = models.get_teacher_classrooms(user["id"])
    classroom_ids = [c["id"] for c in classrooms]

    if classroom_ids:
        placeholders = ",".join("?" * len(classroom_ids))
        rows = conn.execute(
            f"SELECT n.*, "
            f"nominator.display_name as nominator_name, "
            f"nominee.display_name as nominee_name "
            f"FROM nominations n "
            f"JOIN users nominator ON n.nominator_id = nominator.id "
            f"JOIN users nominee ON n.nominee_id = nominee.id "
            f"WHERE n.status != 'pending' AND nominee.classroom_id IN ({placeholders}) "
            f"ORDER BY n.reviewed_at DESC LIMIT 20",
            classroom_ids,
        ).fetchall()
        conn.close()

        if rows:
            for row in rows:
                r = dict(row)
                icon = "✅" if r["status"] == "approved" else "❌"
                st.write(f"{icon} **{r['nominator_name']}** nominated **{r['nominee_name']}** "
                         f"- {r['status'].upper()}")
                st.caption(f"Reason: {r['reason']}")
                if r.get("review_note"):
                    st.caption(f"Note: {r['review_note']}")
                st.markdown("---")
        else:
            st.info("No reviewed nominations yet.")
    else:
        conn.close()
        st.info("No classrooms assigned.")
