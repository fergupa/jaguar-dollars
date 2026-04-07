"""Manage Students - add, edit, and deactivate students."""

import streamlit as st
from auth import require_role
import models

require_role("teacher")
user = st.session_state.user

st.title("👨‍🎓 Manage Students")

# Get teacher's classrooms
classrooms = models.get_teacher_classrooms(user["id"])
if not classrooms:
    st.warning("You don't have any classrooms assigned.")
    st.stop()

# Classroom filter
classroom_options = {c["name"]: c["id"] for c in classrooms}
selected_classroom_name = st.selectbox(
    "Select Classroom",
    options=list(classroom_options.keys())
)
selected_classroom_id = classroom_options[selected_classroom_name]

st.markdown("---")

# ── Add Student Form ───────────────────────────────────────────────────
with st.expander("➕ Add New Student", expanded=False):
    with st.form("add_student", clear_on_submit=True):
        display_name = st.text_input("Student Name", placeholder="e.g., John Smith")
        grade = st.selectbox("Grade", options=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])
        
        if st.form_submit_button("Add Student", use_container_width=True):
            if display_name.strip():
                success, username, student_id = models.create_student(
                    display_name.strip(), grade, selected_classroom_id
                )
                if success:
                    st.success(f"Created student '{display_name}' with username: **{username}** (password: password)")
                    st.rerun()
                else:
                    st.error(f"Failed to create student: {username}")
            else:
                st.warning("Please enter student name.")

st.markdown("---")

# ── Student List ───────────────────────────────────────────────────────
st.subheader("Students")

students = models.get_students_with_details(selected_classroom_id)

if not students:
    st.info("No students in this classroom yet. Add one above!")
else:
    # Show active/inactive filter
    show_inactive = st.checkbox("Show inactive students", value=False)
    
    for student in students:
        # Skip inactive unless showing them
        if not student.get("active", 1) and not show_inactive:
            continue
            
        status_icon = "✅" if student.get("active", 1) else "❌"
        
        with st.expander(f"{status_icon} {student['display_name']} (@{student['username']}) - Grade {student.get('grade', 'N/A')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Balance:** ${student['balance']}")
                st.write(f"**Username:** {student['username']}")
                st.write(f"**Grade:** {student.get('grade', 'Not set')}")
                st.write(f"**Status:** {'Active' if student.get('active', 1) else 'Inactive'}")
            
            with col2:
                # Edit form
                with st.form(f"edit_{student['id']}"):
                    new_name = st.text_input("Name", value=student['display_name'], key=f"name_{student['id']}")
                    new_grade = st.selectbox(
                        "Grade",
                        options=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                        index=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"].index(student.get('grade', 'K')) if student.get('grade') in ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"] else 0,
                        key=f"grade_{student['id']}"
                    )
                    new_username = st.text_input("Username", value=student['username'], key=f"user_{student['id']}")
                    
                    if st.form_submit_button("Save Changes"):
                        success, msg = models.update_student(student['id'], new_name, new_grade, new_username)
                        if success:
                            st.success("Updated!")
                            st.rerun()
                        else:
                            st.error(msg)
            
            # Action buttons
            st.markdown("---")
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            
            with btn_col1:
                if st.button("🔑 Reset Password", key=f"reset_{student['id']}"):
                    if models.reset_student_password(student['id']):
                        st.success("Password reset to 'password'")
                    else:
                        st.error("Failed to reset password")
            
            with btn_col2:
                if student.get("active", 1):
                    if st.button("⏸️ Deactivate", key=f"deact_{student['id']}"):
                        if models.deactivate_student(student['id']):
                            st.success("Student deactivated")
                            st.rerun()
                else:
                    if st.button("▶️ Reactivate", key=f"react_{student['id']}"):
                        conn = models.get_connection()
                        conn.execute("UPDATE users SET active = 1 WHERE id = ?", (student['id'],))
                        conn.commit()
                        conn.close()
                        st.success("Student reactivated")
                        st.rerun()
            
            with btn_col3:
                if st.button("🗑️ Delete", key=f"del_{student['id']}", type="secondary"):
                    success, msg = models.delete_student(student['id'])
                    if success:
                        st.success("Student deleted")
                        st.rerun()
                    else:
                        st.warning(msg)
