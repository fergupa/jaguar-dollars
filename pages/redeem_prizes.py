"""Prize Store - browse and redeem prizes."""

import streamlit as st
from auth import require_role
import models

require_role("student")
user = st.session_state.user

st.title("🎁 Prize Store")

balance = models.get_balance(user["id"])
st.info(f"Your balance: **${balance}**")

prizes = models.list_prizes(prize_type="individual")

if not prizes:
    st.info("No prizes available right now. Check back later!")
    st.stop()

# ── Prize Grid ─────────────────────────────────────────────────────────
cols = st.columns(3)
for i, prize in enumerate(prizes):
    with cols[i % 3]:
        can_afford = balance >= prize["cost"]
        qty_text = "" if prize["quantity"] == -1 else f" ({prize['quantity']} left)"

        with st.container(border=True):
            st.markdown(f"### {prize['emoji']} {prize['name']}")
            st.write(prize["description"])
            st.markdown(f"**${prize['cost']}**{qty_text}")

            if can_afford:
                if st.button("Redeem", key=f"redeem_{prize['id']}", use_container_width=True):
                    st.session_state[f"confirm_{prize['id']}"] = True

                if st.session_state.get(f"confirm_{prize['id']}"):
                    st.warning(f"Spend ${prize['cost']} on {prize['name']}?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("Yes!", key=f"yes_{prize['id']}"):
                            success, msg = models.redeem_prize(user["id"], prize["id"])
                            if success:
                                st.success(msg)
                                st.session_state.pop(f"confirm_{prize['id']}", None)
                                st.rerun()
                            else:
                                st.error(msg)
                    with col_no:
                        if st.button("Cancel", key=f"no_{prize['id']}"):
                            st.session_state.pop(f"confirm_{prize['id']}", None)
                            st.rerun()
            else:
                remaining = prize["cost"] - balance
                st.caption(f"Need ${remaining} more")
