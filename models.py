"""Data access functions for Jaguar Dollars.

All mutating functions use transactions to keep balances consistent.
"""

from datetime import datetime
from database import get_connection
from auth import hash_password


# ── Users ──────────────────────────────────────────────────────────────

def get_user(user_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_students() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT u.*, sb.balance FROM users u "
        "JOIN student_balances sb ON u.id = sb.student_id "
        "WHERE u.role = 'student' ORDER BY u.display_name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_students_by_classroom(classroom_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT u.*, sb.balance FROM users u "
        "JOIN student_balances sb ON u.id = sb.student_id "
        "WHERE u.role = 'student' AND u.classroom_id = ? "
        "ORDER BY u.display_name",
        (classroom_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_classrooms() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT c.*, u.display_name as teacher_name FROM classrooms c "
        "LEFT JOIN users u ON c.teacher_id = u.id ORDER BY c.name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_classroom(classroom_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT c.*, u.display_name as teacher_name FROM classrooms c "
        "LEFT JOIN users u ON c.teacher_id = u.id WHERE c.id = ?",
        (classroom_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_teacher_classrooms(teacher_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM classrooms WHERE teacher_id = ? ORDER BY name",
        (teacher_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Teacher Bank ───────────────────────────────────────────────────────

def get_bank_balance(teacher_id: int) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT balance FROM teacher_banks WHERE teacher_id = ?", (teacher_id,)
    ).fetchone()
    conn.close()
    return row["balance"] if row else 0


def get_bank_info(teacher_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM teacher_banks WHERE teacher_id = ?", (teacher_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def refill_teacher_bank(teacher_id: int, amount: int, reason: str = "") -> bool:
    if amount <= 0 or amount > 10000:
        return False
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE teacher_banks SET balance = balance + ? WHERE teacher_id = ?",
            (amount, teacher_id),
        )
        conn.execute(
            "INSERT INTO bank_adjustments (teacher_id, amount, reason) VALUES (?, ?, ?)",
            (teacher_id, amount, reason),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def get_bank_adjustments(teacher_id: int, limit: int = 10) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM bank_adjustments WHERE teacher_id = ? ORDER BY created_at DESC LIMIT ?",
        (teacher_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Student Balance ────────────────────────────────────────────────────

def get_balance(student_id: int) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT balance FROM student_balances WHERE student_id = ?", (student_id,)
    ).fetchone()
    conn.close()
    return row["balance"] if row else 0


# ── Awards ─────────────────────────────────────────────────────────────

def award_dollars(teacher_id: int, student_id: int, amount: int, note: str = "") -> bool:
    conn = get_connection()
    try:
        bank = conn.execute(
            "SELECT balance FROM teacher_banks WHERE teacher_id = ?", (teacher_id,)
        ).fetchone()
        if not bank or bank["balance"] < amount:
            conn.close()
            return False

        conn.execute(
            "UPDATE teacher_banks SET balance = balance - ?, total_issued = total_issued + ? "
            "WHERE teacher_id = ?",
            (amount, amount, teacher_id),
        )
        conn.execute(
            "UPDATE student_balances SET balance = balance + ? WHERE student_id = ?",
            (amount, student_id),
        )

        student = conn.execute(
            "SELECT classroom_id FROM users WHERE id = ?", (student_id,)
        ).fetchone()

        conn.execute(
            "INSERT INTO transactions (type, from_user_id, to_user_id, amount, note, classroom_id) "
            "VALUES ('award', ?, ?, ?, ?, ?)",
            (teacher_id, student_id, amount, note, student["classroom_id"] if student else None),
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


# ── Prizes ─────────────────────────────────────────────────────────────

def list_prizes(prize_type: str | None = None, active_only: bool = True) -> list[dict]:
    conn = get_connection()
    query = "SELECT * FROM prizes"
    params = []
    conditions = []

    if prize_type:
        conditions.append("prize_type = ?")
        params.append(prize_type)
    if active_only:
        conditions.append("active = 1")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY cost"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_prize(name: str, description: str, cost: int, prize_type: str,
                 quantity: int = -1, emoji: str = "🎁") -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO prizes (name, description, cost, prize_type, quantity, emoji) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (name, description, cost, prize_type, quantity, emoji),
    )
    conn.commit()
    prize_id = cursor.lastrowid
    conn.close()
    return prize_id


def update_prize(prize_id: int, **kwargs):
    conn = get_connection()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    conn.execute(f"UPDATE prizes SET {sets} WHERE id = ?", (*kwargs.values(), prize_id))
    conn.commit()
    conn.close()


def toggle_prize(prize_id: int):
    conn = get_connection()
    conn.execute("UPDATE prizes SET active = 1 - active WHERE id = ?", (prize_id,))
    conn.commit()
    conn.close()


def redeem_prize(student_id: int, prize_id: int) -> tuple[bool, str]:
    conn = get_connection()
    try:
        prize = conn.execute("SELECT * FROM prizes WHERE id = ? AND active = 1", (prize_id,)).fetchone()
        if not prize:
            return False, "Prize not found or inactive."

        balance = conn.execute(
            "SELECT balance FROM student_balances WHERE student_id = ?", (student_id,)
        ).fetchone()
        if not balance or balance["balance"] < prize["cost"]:
            return False, "Not enough Jaguar Dollars!"

        if prize["quantity"] != -1 and prize["quantity"] <= 0:
            return False, "Prize is out of stock."

        conn.execute(
            "UPDATE student_balances SET balance = balance - ? WHERE student_id = ?",
            (prize["cost"], student_id),
        )

        if prize["quantity"] != -1:
            conn.execute(
                "UPDATE prizes SET quantity = quantity - 1 WHERE id = ?", (prize_id,)
            )

        student = conn.execute(
            "SELECT classroom_id FROM users WHERE id = ?", (student_id,)
        ).fetchone()

        conn.execute(
            "INSERT INTO transactions (type, from_user_id, to_user_id, amount, note, classroom_id) "
            "VALUES ('redemption', ?, NULL, ?, ?, ?)",
            (student_id, prize["cost"], f"Redeemed: {prize['name']}", student["classroom_id"] if student else None),
        )
        conn.commit()
        return True, f"You redeemed {prize['name']}!"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


# ── Nominations ────────────────────────────────────────────────────────

def create_nomination(nominator_id: int, nominee_id: int, reason: str,
                      suggested_amount: int = 5) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO nominations (nominator_id, nominee_id, reason, suggested_amount) "
        "VALUES (?, ?, ?, ?)",
        (nominator_id, nominee_id, reason, suggested_amount),
    )
    conn.commit()
    nom_id = cursor.lastrowid
    conn.close()
    return nom_id


def get_pending_nominations(classroom_id: int | None = None) -> list[dict]:
    conn = get_connection()
    query = (
        "SELECT n.*, "
        "nominator.display_name as nominator_name, "
        "nominee.display_name as nominee_name, "
        "nominee.classroom_id as nominee_classroom_id "
        "FROM nominations n "
        "JOIN users nominator ON n.nominator_id = nominator.id "
        "JOIN users nominee ON n.nominee_id = nominee.id "
        "WHERE n.status = 'pending'"
    )
    params = []
    if classroom_id:
        query += " AND nominee.classroom_id = ?"
        params.append(classroom_id)
    query += " ORDER BY n.created_at DESC"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_nominations_by_user(user_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT n.*, nominee.display_name as nominee_name "
        "FROM nominations n "
        "JOIN users nominee ON n.nominee_id = nominee.id "
        "WHERE n.nominator_id = ? ORDER BY n.created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def review_nomination(nomination_id: int, teacher_id: int, status: str,
                      review_note: str = "", amount: int | None = None) -> bool:
    conn = get_connection()
    try:
        nom = conn.execute(
            "SELECT * FROM nominations WHERE id = ? AND status = 'pending'",
            (nomination_id,),
        ).fetchone()
        if not nom:
            return False

        conn.execute(
            "UPDATE nominations SET status = ?, reviewed_by = ?, review_note = ?, "
            "reviewed_at = ? WHERE id = ?",
            (status, teacher_id, review_note, datetime.now().isoformat(), nomination_id),
        )

        if status == "approved":
            award_amount = amount if amount else nom["suggested_amount"]
            conn.commit()
            conn.close()
            return award_dollars(teacher_id, nom["nominee_id"], award_amount,
                                f"Nomination by peer: {nom['reason'][:50]}")

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ── Classroom Pool ─────────────────────────────────────────────────────

def contribute_to_pool(student_id: int, classroom_id: int, amount: int) -> tuple[bool, str]:
    conn = get_connection()
    try:
        balance = conn.execute(
            "SELECT balance FROM student_balances WHERE student_id = ?", (student_id,)
        ).fetchone()
        if not balance or balance["balance"] < amount:
            return False, "Not enough Jaguar Dollars!"

        conn.execute(
            "UPDATE student_balances SET balance = balance - ? WHERE student_id = ?",
            (amount, student_id),
        )
        conn.execute(
            "UPDATE classrooms SET pool_balance = pool_balance + ? WHERE id = ?",
            (amount, classroom_id),
        )
        conn.execute(
            "INSERT INTO transactions (type, from_user_id, to_user_id, amount, note, classroom_id) "
            "VALUES ('pool_contrib', ?, NULL, ?, 'Contributed to class pool', ?)",
            (student_id, amount, classroom_id),
        )
        conn.commit()
        return True, f"You contributed {amount} Jaguar Dollars to the class pool!"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def redeem_class_prize(classroom_id: int, prize_id: int, teacher_id: int) -> tuple[bool, str]:
    conn = get_connection()
    try:
        prize = conn.execute("SELECT * FROM prizes WHERE id = ? AND active = 1", (prize_id,)).fetchone()
        if not prize:
            return False, "Prize not found or inactive."

        classroom = conn.execute(
            "SELECT pool_balance FROM classrooms WHERE id = ?", (classroom_id,)
        ).fetchone()
        if not classroom or classroom["pool_balance"] < prize["cost"]:
            return False, "Not enough dollars in the class pool!"

        conn.execute(
            "UPDATE classrooms SET pool_balance = pool_balance - ? WHERE id = ?",
            (prize["cost"], classroom_id),
        )
        conn.execute(
            "INSERT INTO transactions (type, from_user_id, to_user_id, amount, note, classroom_id) "
            "VALUES ('pool_redemption', ?, NULL, ?, ?, ?)",
            (teacher_id, prize["cost"], f"Class prize: {prize['name']}", classroom_id),
        )
        conn.commit()
        return True, f"Class prize '{prize['name']}' redeemed!"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


# ── Transactions ───────────────────────────────────────────────────────

def get_transactions(user_id: int | None = None, classroom_id: int | None = None,
                     txn_type: str | None = None, limit: int = 50) -> list[dict]:
    conn = get_connection()
    query = (
        "SELECT t.*, "
        "from_u.display_name as from_name, "
        "to_u.display_name as to_name "
        "FROM transactions t "
        "LEFT JOIN users from_u ON t.from_user_id = from_u.id "
        "LEFT JOIN users to_u ON t.to_user_id = to_u.id "
    )
    conditions = []
    params = []

    if user_id:
        conditions.append("(t.from_user_id = ? OR t.to_user_id = ?)")
        params.extend([user_id, user_id])
    if classroom_id:
        conditions.append("t.classroom_id = ?")
        params.append(classroom_id)
    if txn_type:
        conditions.append("t.type = ?")
        params.append(txn_type)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY t.created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pool_contributions(classroom_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT u.display_name, SUM(t.amount) as total_contributed "
        "FROM transactions t "
        "JOIN users u ON t.from_user_id = u.id "
        "WHERE t.type = 'pool_contrib' AND t.classroom_id = ? "
        "GROUP BY t.from_user_id ORDER BY total_contributed DESC",
        (classroom_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Student Management ─────────────────────────────────────────────────

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
