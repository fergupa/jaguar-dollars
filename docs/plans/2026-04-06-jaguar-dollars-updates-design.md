# Jaguar Dollars Updates Design

**Date:** 2026-04-06  
**Status:** Approved

## Overview

Three changes to the Jaguar Dollars reward system:
1. Rename mascot from Gator to Jaguar
2. Add student management screen for teachers
3. Add Rob Canada as demo teacher

---

## 1. Mascot Rename (Gator → Jaguar)

Replace all "Gator" references with "Jaguar" across:
- UI text and headers
- Variable names and comments  
- Database seed data
- README and documentation

---

## 2. Student Management Screen

### New Page
`pages/manage_students.py` — teacher-only access

### Database Changes
Add to `users` table:
- `grade` (TEXT, nullable) — student's grade level
- `active` (BOOLEAN, default TRUE) — for soft-delete/deactivation

### UI Layout
- **Table columns:** Student Name, Username, Grade, Teacher/Classroom, Status
- **Filters:** By classroom (teacher's classrooms only)
- **Row actions:** Edit, Reset Password, Deactivate/Delete
- **Add Student form:**
  - Display Name (required)
  - Grade (dropdown: K, 1-12)
  - Username auto-generated as `firstname.lastname` (suffix added if duplicate)
  - Default password: `password`

### Model Functions
- `create_student(display_name, grade, classroom_id)` — auto-generates username/password
- `update_student(student_id, display_name, grade, username)` — edit student details
- `reset_student_password(student_id)` — resets to default password
- `deactivate_student(student_id)` — sets active=FALSE
- `delete_student(student_id)` — hard delete option

### Authorization
- Teachers can only manage students in their own classrooms
- Students cannot access this page

---

## 3. Demo Data: Rob Canada

Add to `seed_data.py`:
- **Teacher:** Rob Canada
  - Username: `rcanada`
  - Password: `password`
- **Classroom:** Assigned to Rob Canada
- Optionally seed a few students for this classroom

---

## Technical Notes

- Grade stored per student (not per classroom) to support mixed-grade classrooms
- Username uniqueness handled via suffix (e.g., `john.smith`, `john.smith2`)
- Soft delete preferred (deactivate) to preserve transaction history integrity
