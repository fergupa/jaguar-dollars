"""Student Dashboard - balance display and recent activity."""

import streamlit as st
from auth import require_role
import models

require_role("student")
user = st.session_state.user

st.title("🐊 My Gator Dollars")

# ── Balance Display ────────────────────────────────────────────────────
balance = models.get_balance(user["id"])
st.markdown(f"<div class='big-balance'>${balance}</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Your current balance</p>",
            unsafe_allow_html=True)

st.markdown("---")

# ── Goal Tracker ───────────────────────────────────────────────────────
prizes = models.list_prizes(prize_type="individual")
if prizes:
    st.subheader("Goal Tracker")
    prize_options = {f"{p['emoji']} {p['name']} (${p['cost']})": p for p in prizes}

    goal_key = "student_goal"
    if goal_key not in st.session_state:
        st.session_state[goal_key] = list(prize_options.keys())[0]

    selected_goal = st.selectbox("I'm saving for...", options=list(prize_options.keys()),
                                 key=goal_key)
    goal_prize = prize_options[selected_goal]
    progress = min(balance / goal_prize["cost"], 1.0) if goal_prize["cost"] > 0 else 1.0
    st.progress(progress)

    remaining = max(goal_prize["cost"] - balance, 0)
    if remaining > 0:
        st.caption(f"${remaining} more to go!")
    else:
        st.success("You can afford this! Head to the Prize Store to redeem it.")

st.markdown("---")

# ── Recent Activity ────────────────────────────────────────────────────
st.subheader("Recent Activity")

txns = models.get_transactions(user_id=user["id"], limit=10)
if txns:
    for txn in txns:
        icon = {"award": "💰", "redemption": "🎁", "pool_contrib": "🏊",
                "nomination_award": "⭐"}.get(txn["type"], "📋")

        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.write(icon)
        with col2:
            if txn["type"] == "award":
                st.write(f"Received **${txn['amount']}** from **{txn['from_name']}**")
                st.caption(txn["note"] or "")
            elif txn["type"] == "redemption":
                st.write(f"Spent **${txn['amount']}**")
                st.caption(txn["note"] or "")
            elif txn["type"] == "pool_contrib":
                st.write(f"Contributed **${txn['amount']}** to class pool")
            elif txn["type"] == "nomination_award":
                st.write(f"Received **${txn['amount']}** from peer nomination")
                st.caption(txn["note"] or "")
            else:
                st.write(f"${txn['amount']} - {txn['note']}")
        with col3:
            if txn["type"] in ("award", "nomination_award") and txn["to_user_id"] == user["id"]:
                st.write(f"+${txn['amount']}")
            else:
                st.write(f"-${txn['amount']}")
else:
    st.info("No activity yet. Earn some Gator Dollars!")
