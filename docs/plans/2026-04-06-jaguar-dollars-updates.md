# Jaguar Dollars Updates Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rename Gator to Jaguar, add student management for teachers, add Rob Canada as demo teacher.

**Architecture:** Three independent changes: (1) text/file replacements for mascot rename, (2) new database columns + page + model functions for student management, (3) seed data additions for new teacher.

**Tech Stack:** Python, Streamlit, SQLite3

---

## Task 1: Rename Database File Reference

**Files:**
- Modify: `database.py:6`

**Step 1: Update DB_PATH constant**

Change `gator_dollars.db` to `jaguar_dollars.db`:

```python
DB_PATH = Path(__file__).parent / "jaguar_dollars.db"
```

**Step 2: Update docstring**

Change line 1 from "Gator Dollars" to "Jaguar Dollars".

**Step 3: Commit**

```bash
git add database.py
git commit -m "refactor: rename database file to jaguar_dollars.db"
```

---

## Task 2: Rename Mascot in models.py

**Files:**
- Modify: `models.py:1`, `models.py:208`, `models.py:338`, `models.py:354`

**Step 1: Update docstring (line 1)**

Change "Gator Dollars" to "Jaguar Dollars".

**Step 2: Update error messages and strings**

- Line 208: `"Not enough Gator Dollars!"` → `"Not enough Jaguar Dollars!"`
- Line 338: `"Not enough Gator Dollars!"` → `"Not enough Jaguar Dollars!"`
- Line 354: `"Gator Dollars"` → `"Jaguar Dollars"`

**Step 3: Commit**

```bash
git add models.py
git commit -m "refactor: rename Gator to Jaguar in models.py"
```

---

## Task 3: Rename Mascot in app.py

**Files:**
- Modify: `app.py`

**Step 1: Update all Gator references**

- Line 1 docstring: "Gator Dollars" → "Jaguar Dollars"
- Line 15 page_title: "Gator Dollars" → "Jaguar Dollars"
- Line 16 page_icon: "🐊" → "🐆"
- Line 40 CSS class: `.gator-header` → `.jaguar-header`
- Line 57 header: "🐊 Gator Dollars" → "🐆 Jaguar Dollars"
- Line 85-87 demo credentials: change passwords from `gator123` to `jaguar123`
- Line 101 sidebar: "🐊 Gator Dollars" → "🐆 Jaguar Dollars"
- Line 130 student nav: "My Gator Dollars" with "🐊" → "My Jaguar Dollars" with "🐆"

**Step 2: Commit**

```bash
git add app.py
git commit -m "refactor: rename Gator to Jaguar in app.py"
```

---

## Task 4: Rename Mascot in Page Files

**Files:**
- Modify: `pages/student_dashboard.py`, `pages/teacher_dashboard.py`, `pages/nominate_peer.py`, `pages/transaction_history.py`

**Step 1: Update student_dashboard.py**

- Line 10 title: "🐊 My Gator Dollars" → "🐆 My Jaguar Dollars"

**Step 2: Update teacher_dashboard.py**

- Line 49 button text: "Award Gator Dollars" → "Award Jaguar Dollars"

**Step 3: Update nominate_peer.py**

- Line 1 docstring: "Gator Dollars" → "Jaguar Dollars"
- Line 12-13: "Gator Dollars" → "Jaguar Dollars"
- Line 30 slider label: "Gator Dollars" → "Jaguar Dollars"

**Step 4: Update transaction_history.py**

- Line 1 docstring: "Gator Dollar" → "Jaguar Dollar"

**Step 5: Commit**

```bash
git add pages/
git commit -m "refactor: rename Gator to Jaguar in page files"
```

---

## Task 5: Update seed_data.py - Mascot Rename and Add Rob Canada

**Files:**
- Modify: `seed_data.py`

**Step 1: Update docstring (line 1)**

Change "Gator Dollars" to "Jaguar Dollars".

**Step 2: Change teacher passwords from gator123 to jaguar123**

Line 27-29: Update password from "gator123" to "jaguar123".

**Step 3: Add Rob Canada as 4th teacher with classroom**

After existing classrooms list, add:
```python
("Room 405 - Social Studies", None),
```

After existing teachers list, add:
```python
("rcanada", "jaguar123", "Rob Canada", classroom_ids[3]),
```

**Step 4: Commit**

```bash
git add seed_data.py
git commit -m "refactor: rename Gator to Jaguar, add Rob Canada teacher"
```

---

## Task 6: Update README.md

**Files:**
- Modify: `README.md`

**Step 1: Update all Gator references to Jaguar**

- Line 1: "# Gator Dollars" → "# Jaguar Dollars"
- Line 3: "Gator Dollars" → "Jaguar Dollars"
- Line 20-22: passwords "gator123" → "jaguar123"
- Line 53: "My Gator Dollars" → "My Jaguar Dollars"
- Line 55: "Gator Dollars" → "Jaguar Dollars"
- Line 61: "Gator Dollars" → "Jaguar Dollars"
- Line 69: "gator_dollars.db" → "jaguar_dollars.db"

**Step 2: Add Rob Canada to teachers table**

Add row: `| rcanada | jaguar123 | Rob Canada | Room 405 - Social Studies |`

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: update README with Jaguar branding and Rob Canada"
```

---

## Task 7: Add Grade and Active Columns to Database Schema

**Files:**
- Modify: `database.py`

**Step 1: Add new columns to users table schema**

In the CREATE TABLE users statement, add after `created_at`:
```sql
grade         TEXT,
active        INTEGER DEFAULT 1
```

**Step 2: Commit**

```bash
git add database.py
git commit -m "feat: add grade and active columns to users table"
```

---

## Task 8: Add Student Management Model Functions

**Files:**
- Modify: `models.py`

**Step 1: Add import for hashlib**

At the top of models.py, add:
```python
from auth import hash_password
```

**Step 2: Add generate_username helper function**

```python
def generate_username(display_name: str) -> str:
    """Generate username from display name (firstname.lastname), handling duplicates."""
    conn = get_connection()
    parts = display_name.lower().strip().split()
    if len(parts) >= 2:
        base_username = f"{parts[0]}.{parts[-1]}"
    else:
        base_username = parts[0] if parts else "student"
    
    # Check for duplicates
    username = base_username
    suffix = 2
    while True:
        exists = conn.execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        ).fetchone()
        if not exists:
            break
        username = f"{base_username}{suffix}"
        suffix += 1
    
    conn.close()
    return username
```

**Step 3: Add create_student function**

```python
def create_student(display_name: str, grade: str, classroom_id: int) -> tuple[bool, str, int | None]:
    """Create a new student with auto-generated username and default password."""
    conn = get_connection()
    try:
        username = generate_username(display_name)
        password_hash = hash_password("password")
        
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, display_name, role, classroom_id, grade, active) "
            "VALUES (?, ?, ?, 'student', ?, ?, 1)",
            (username, password_hash, display_name, classroom_id, grade),
        )
        student_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO student_balances (student_id, balance) VALUES (?, 0)",
            (student_id,),
        )
        conn.commit()
        return True, username, student_id
    except Exception as e:
        conn.rollback()
        return False, str(e), None
    finally:
        conn.close()
```

**Step 4: Add update_student function**

```python
def update_student(student_id: int, display_name: str, grade: str, username: str) -> tuple[bool, str]:
    """Update student details."""
    conn = get_connection()
    try:
        # Check username uniqueness (excluding current student)
        exists = conn.execute(
            "SELECT 1 FROM users WHERE username = ? AND id != ?",
            (username, student_id),
        ).fetchone()
        if exists:
            return False, "Username already taken"
        
        conn.execute(
            "UPDATE users SET display_name = ?, grade = ?, username = ? WHERE id = ?",
            (display_name, grade, username, student_id),
        )
        conn.commit()
        return True, "Student updated successfully"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()
```

**Step 5: Add reset_student_password function**

```python
def reset_student_password(student_id: int) -> bool:
    """Reset student password to default 'password'."""
    conn = get_connection()
    try:
        password_hash = hash_password("password")
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, student_id),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()
```

**Step 6: Add deactivate_student function**

```python
def deactivate_student(student_id: int) -> bool:
    """Deactivate a student (soft delete)."""
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET active = 0 WHERE id = ?", (student_id,))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()
```

**Step 7: Add delete_student function**

```python
def delete_student(student_id: int) -> tuple[bool, str]:
    """Hard delete a student. Will fail if student has transaction history."""
    conn = get_connection()
    try:
        # Check for transactions
        has_txns = conn.execute(
            "SELECT 1 FROM transactions WHERE from_user_id = ? OR to_user_id = ?",
            (student_id, student_id),
        ).fetchone()
        if has_txns:
            return False, "Cannot delete student with transaction history. Use deactivate instead."
        
        conn.execute("DELETE FROM student_balances WHERE student_id = ?", (student_id,))
        conn.execute("DELETE FROM nominations WHERE nominator_id = ? OR nominee_id = ?", (student_id, student_id))
        conn.execute("DELETE FROM users WHERE id = ?", (student_id,))
        conn.commit()
        return True, "Student deleted"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()
```

**Step 8: Add get_students_with_details function**

```python
def get_students_with_details(classroom_id: int | None = None) -> list[dict]:
    """Get students with grade, balance, and classroom info."""
    conn = get_connection()
    query = """
        SELECT u.*, sb.balance, c.name as classroom_name,
               (SELECT display_name FROM users WHERE id = c.teacher_id) as teacher_name
        FROM users u
        JOIN student_balances sb ON u.id = sb.student_id
        JOIN classrooms c ON u.classroom_id = c.id
        WHERE u.role = 'student'
    """
    params = []
    if classroom_id:
        query += " AND u.classroom_id = ?"
        params.append(classroom_id)
    query += " ORDER BY u.display_name"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
```

**Step 9: Commit**

```bash
git add models.py
git commit -m "feat: add student management model functions"
```

---

## Task 9: Create Student Management Page

**Files:**
- Create: `pages/manage_students.py`

**Step 1: Create the page file**

```python
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
```

**Step 2: Commit**

```bash
git add pages/manage_students.py
git commit -m "feat: add student management page"
```

---

## Task 10: Add Student Management to Navigation

**Files:**
- Modify: `app.py`

**Step 1: Add new page to teacher navigation**

In the teacher pages list (around line 120), add after "Give Dollars":
```python
st.Page("pages/manage_students.py", title="Manage Students", icon="👨‍🎓"),
```

**Step 2: Commit**

```bash
git add app.py
git commit -m "feat: add manage students to teacher navigation"
```

---

## Task 11: Delete Old Database and Test

**Step 1: Delete old database file**

```bash
rm gator_dollars.db 2>$null; rm jaguar_dollars.db 2>$null
```

**Step 2: Start app and verify**

```bash
streamlit run app.py
```

**Step 3: Manual verification checklist**

- [ ] Login page shows "Jaguar Dollars" with 🐆 icon
- [ ] Demo credentials show jaguar123 password
- [ ] Teacher can login with mrivera/jaguar123
- [ ] Rob Canada appears as teacher (rcanada/jaguar123)
- [ ] Sidebar shows "Jaguar Dollars"
- [ ] "Manage Students" appears in teacher nav
- [ ] Can add new student with auto-generated username
- [ ] Can edit student name, grade, username
- [ ] Can reset password
- [ ] Can deactivate/delete student
- [ ] Student dashboard shows "My Jaguar Dollars"

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete Jaguar Dollars updates - mascot rename, student management, Rob Canada"
```

---

## Summary

| Task | Description | Est. Time |
|------|-------------|-----------|
| 1 | Rename database file reference | 2 min |
| 2 | Rename mascot in models.py | 3 min |
| 3 | Rename mascot in app.py | 5 min |
| 4 | Rename mascot in page files | 5 min |
| 5 | Update seed_data.py + Rob Canada | 5 min |
| 6 | Update README.md | 3 min |
| 7 | Add database columns | 2 min |
| 8 | Add model functions | 10 min |
| 9 | Create manage_students.py | 10 min |
| 10 | Add to navigation | 2 min |
| 11 | Test and verify | 5 min |

**Total estimated time: ~50 minutes**
