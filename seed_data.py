"""Seed the database with demo data for Gator Dollars."""

import random
from datetime import datetime, timedelta
from database import init_db, get_connection
from auth import hash_password


def seed():
    init_db()
    conn = get_connection()

    # Check if already seeded
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        print("Database already seeded. Delete gator_dollars.db to re-seed.")
        conn.close()
        return

    # ── Classrooms ─────────────────────────────────────────────────────
    classrooms = [
        ("Room 204 - Science", None),
        ("Room 112 - English", None),
        ("Room 301 - Math", None),
    ]
    classroom_ids = []
    for name, _ in classrooms:
        cursor = conn.execute("INSERT INTO classrooms (name) VALUES (?)", (name,))
        classroom_ids.append(cursor.lastrowid)

    # ── Teachers ───────────────────────────────────────────────────────
    teachers = [
        ("mrivera", "gator123", "Mrs. Rivera", classroom_ids[0]),
        ("mthompson", "gator123", "Mr. Thompson", classroom_ids[1]),
        ("mchen", "gator123", "Ms. Chen", classroom_ids[2]),
    ]
    teacher_ids = []
    for username, password, name, cid in teachers:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, display_name, role, classroom_id) "
            "VALUES (?, ?, ?, 'teacher', ?)",
            (username, hash_password(password), name, cid),
        )
        tid = cursor.lastrowid
        teacher_ids.append(tid)
        conn.execute("INSERT INTO teacher_banks (teacher_id, balance, total_issued) VALUES (?, 500, 0)", (tid,))

    # Link classrooms to teachers
    for i, cid in enumerate(classroom_ids):
        conn.execute("UPDATE classrooms SET teacher_id = ? WHERE id = ?", (teacher_ids[i], cid))

    # ── Students ───────────────────────────────────────────────────────
    student_data = [
        # Room 204 - Science (Mrs. Rivera)
        ("jsmith", "student", "Jordan Smith", classroom_ids[0]),
        ("agarcia", "student", "Alex Garcia", classroom_ids[0]),
        ("mwilson", "student", "Maya Wilson", classroom_ids[0]),
        ("dlee", "student", "David Lee", classroom_ids[0]),
        ("sbrooks", "student", "Sofia Brooks", classroom_ids[0]),
        # Room 112 - English (Mr. Thompson)
        ("tjohnson", "student", "Tyler Johnson", classroom_ids[1]),
        ("kpatel", "student", "Kira Patel", classroom_ids[1]),
        ("rmartin", "student", "Ryan Martin", classroom_ids[1]),
        ("enguyen", "student", "Emma Nguyen", classroom_ids[1]),
        ("jwilliams", "student", "Jake Williams", classroom_ids[1]),
        # Room 301 - Math (Ms. Chen)
        ("lrodriguez", "student", "Lily Rodriguez", classroom_ids[2]),
        ("okim", "student", "Owen Kim", classroom_ids[2]),
        ("cjones", "student", "Chloe Jones", classroom_ids[2]),
        ("abrown", "student", "Aiden Brown", classroom_ids[2]),
        ("zthomas", "student", "Zoe Thomas", classroom_ids[2]),
    ]
    student_ids = []
    for username, password, name, cid in student_data:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash, display_name, role, classroom_id) "
            "VALUES (?, ?, ?, 'student', ?)",
            (username, hash_password(password), name, cid),
        )
        sid = cursor.lastrowid
        student_ids.append(sid)
        conn.execute("INSERT INTO student_balances (student_id, balance) VALUES (?, 0)", (sid,))

    # ── Prizes ─────────────────────────────────────────────────────────
    prizes = [
        ("Sticker Pack", "A pack of cool holographic stickers", 5, "individual", -1, "🌟"),
        ("Ice Cream Sundae", "Your choice of ice cream from the cafeteria", 15, "individual", -1, "🍦"),
        ("Homework Pass", "Skip one homework assignment", 20, "individual", 10, "📝"),
        ("Extra Recess", "15 extra minutes of recess", 25, "individual", -1, "🏃"),
        ("Lunch with Principal", "Special lunch in the principal's office", 40, "individual", 5, "🍕"),
        ("Class Game Hour", "One hour of games for the whole class", 100, "classroom", -1, "🎮"),
        ("Class Movie Day", "Movie and popcorn for the class", 150, "classroom", -1, "🎬"),
        ("Class Pizza Party", "Pizza party for the whole class!", 200, "classroom", -1, "🍕"),
    ]
    for name, desc, cost, ptype, qty, emoji in prizes:
        conn.execute(
            "INSERT INTO prizes (name, description, cost, prize_type, quantity, emoji) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, desc, cost, ptype, qty, emoji),
        )

    conn.commit()

    # ── Sample Transactions ────────────────────────────────────────────
    now = datetime.now()
    award_reasons = [
        "Great participation in class today!",
        "Helped a classmate with their work",
        "Excellent homework submission",
        "Positive attitude all week",
        "Outstanding test score",
        "Volunteered to help clean up",
        "Great teamwork on group project",
        "Showed leadership during activity",
        "Improved behavior this week",
        "Creative solution on assignment",
    ]

    # Give awards to students (30-40 transactions)
    for i, sid in enumerate(student_ids):
        classroom_idx = i // 5
        teacher_id = teacher_ids[classroom_idx]
        classroom_id = classroom_ids[classroom_idx]

        # Each student gets 2-4 awards
        num_awards = random.randint(2, 4)
        for j in range(num_awards):
            amount = random.choice([5, 5, 10, 10, 10, 15, 15, 20])
            days_ago = random.randint(1, 21)
            reason = random.choice(award_reasons)

            conn.execute(
                "INSERT INTO transactions (type, from_user_id, to_user_id, amount, note, classroom_id, created_at) "
                "VALUES ('award', ?, ?, ?, ?, ?, ?)",
                (teacher_id, sid, amount, reason, classroom_id,
                 (now - timedelta(days=days_ago)).isoformat()),
            )
            conn.execute(
                "UPDATE student_balances SET balance = balance + ? WHERE student_id = ?",
                (amount, sid),
            )
            conn.execute(
                "UPDATE teacher_banks SET balance = balance - ?, total_issued = total_issued + ? "
                "WHERE teacher_id = ?",
                (amount, amount, teacher_id),
            )

    # A few redemptions
    for sid in random.sample(student_ids, 5):
        bal = conn.execute("SELECT balance FROM student_balances WHERE student_id = ?", (sid,)).fetchone()
        if bal and bal["balance"] >= 5:
            classroom_id = conn.execute("SELECT classroom_id FROM users WHERE id = ?", (sid,)).fetchone()["classroom_id"]
            conn.execute(
                "INSERT INTO transactions (type, from_user_id, amount, note, classroom_id, created_at) "
                "VALUES ('redemption', ?, 5, 'Redeemed: Sticker Pack', ?, ?)",
                (sid, classroom_id, (now - timedelta(days=random.randint(1, 7))).isoformat()),
            )
            conn.execute("UPDATE student_balances SET balance = balance - 5 WHERE student_id = ?", (sid,))

    # A few pool contributions
    for cid_idx in range(3):
        contributors = random.sample(student_ids[cid_idx * 5:(cid_idx + 1) * 5], 2)
        for sid in contributors:
            amount = random.choice([5, 10])
            bal = conn.execute("SELECT balance FROM student_balances WHERE student_id = ?", (sid,)).fetchone()
            if bal and bal["balance"] >= amount:
                conn.execute(
                    "INSERT INTO transactions (type, from_user_id, amount, note, classroom_id, created_at) "
                    "VALUES ('pool_contrib', ?, ?, 'Contributed to class pool', ?, ?)",
                    (sid, amount, classroom_ids[cid_idx],
                     (now - timedelta(days=random.randint(1, 5))).isoformat()),
                )
                conn.execute("UPDATE student_balances SET balance = balance - ? WHERE student_id = ?", (amount, sid))
                conn.execute("UPDATE classrooms SET pool_balance = pool_balance + ? WHERE id = ?",
                             (amount, classroom_ids[cid_idx]))

    # Sample nominations
    # Approved nomination
    conn.execute(
        "INSERT INTO nominations (nominator_id, nominee_id, reason, suggested_amount, status, "
        "reviewed_by, review_note, created_at, reviewed_at) "
        "VALUES (?, ?, 'Always helps others with their science projects', 5, 'approved', ?, "
        "'Great nomination!', ?, ?)",
        (student_ids[0], student_ids[1], teacher_ids[0],
         (now - timedelta(days=5)).isoformat(), (now - timedelta(days=4)).isoformat()),
    )
    # Pending nomination
    conn.execute(
        "INSERT INTO nominations (nominator_id, nominee_id, reason, suggested_amount, status, created_at) "
        "VALUES (?, ?, 'Helped me understand fractions during study hall', 5, 'pending', ?)",
        (student_ids[12], student_ids[11], (now - timedelta(days=1)).isoformat()),
    )
    # Denied nomination
    conn.execute(
        "INSERT INTO nominations (nominator_id, nominee_id, reason, suggested_amount, status, "
        "reviewed_by, review_note, created_at, reviewed_at) "
        "VALUES (?, ?, 'They are my friend', 10, 'denied', ?, "
        "'Nominations should be for specific helpful actions', ?, ?)",
        (student_ids[6], student_ids[7], teacher_ids[1],
         (now - timedelta(days=3)).isoformat(), (now - timedelta(days=2)).isoformat()),
    )

    conn.commit()
    conn.close()

    print("Database seeded successfully!")
    print("\nDemo Credentials:")
    print("─" * 40)
    print("TEACHERS:")
    print("  mrivera / gator123   (Mrs. Rivera - Science)")
    print("  mthompson / gator123 (Mr. Thompson - English)")
    print("  mchen / gator123     (Ms. Chen - Math)")
    print("\nSTUDENTS:")
    print("  jsmith / student     (Jordan Smith)")
    print("  agarcia / student    (Alex Garcia)")
    print("  kpatel / student     (Kira Patel)")
    print("  ... and 12 more (all use password 'student')")


if __name__ == "__main__":
    seed()
