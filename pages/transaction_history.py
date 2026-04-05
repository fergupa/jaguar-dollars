"""Transaction History - filterable log of all Gator Dollar activity."""

import streamlit as st
import pandas as pd
import models

user = st.session_state.get("user")
if not user:
    st.error("Please log in.")
    st.stop()

st.title("📋 Transaction History")

# ── Filters ────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    type_options = ["All", "award", "redemption", "pool_contrib", "pool_redemption", "nomination_award"]
    type_labels = {
        "All": "All Types",
        "award": "Awards",
        "redemption": "Redemptions",
        "pool_contrib": "Pool Contributions",
        "pool_redemption": "Pool Redemptions",
        "nomination_award": "Nomination Awards",
    }
    selected_type = st.selectbox("Transaction Type",
                                 options=type_options,
                                 format_func=lambda x: type_labels[x])

with col2:
    limit = st.selectbox("Show", [25, 50, 100], index=1)

txn_type = selected_type if selected_type != "All" else None

# ── Fetch Transactions ─────────────────────────────────────────────────
if user["role"] == "teacher":
    # Teachers see transactions for their classrooms
    classrooms = models.get_teacher_classrooms(user["id"])

    classroom_filter = st.selectbox(
        "Classroom",
        options=["All Classrooms"] + [c["name"] for c in classrooms],
    )

    all_txns = []
    if classroom_filter == "All Classrooms":
        for c in classrooms:
            all_txns.extend(models.get_transactions(classroom_id=c["id"], txn_type=txn_type, limit=limit))
    else:
        cid = next(c["id"] for c in classrooms if c["name"] == classroom_filter)
        all_txns = models.get_transactions(classroom_id=cid, txn_type=txn_type, limit=limit)

    all_txns.sort(key=lambda t: t["created_at"], reverse=True)
    all_txns = all_txns[:limit]
else:
    # Students see only their own transactions
    all_txns = models.get_transactions(user_id=user["id"], txn_type=txn_type, limit=limit)

# ── Display ────────────────────────────────────────────────────────────
if all_txns:
    rows = []
    for txn in all_txns:
        icon = {"award": "💰", "redemption": "🎁", "pool_contrib": "🏊",
                "pool_redemption": "🎉", "nomination_award": "⭐"}.get(txn["type"], "📋")
        rows.append({
            "": icon,
            "Type": type_labels.get(txn["type"], txn["type"]),
            "From": txn["from_name"] or "-",
            "To": txn["to_name"] or "-",
            "Amount": f"${txn['amount']}",
            "Note": txn["note"] or "",
            "Date": txn["created_at"][:16] if txn["created_at"] else "",
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.caption(f"Showing {len(rows)} transaction(s)")
else:
    st.info("No transactions found with the selected filters.")
