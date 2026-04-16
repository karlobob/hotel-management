#from database import get_connection
from hotel.services.database import get_connection


# Retrieves all staff members from the database, ordered by name, and returns them as a list of dictionaries.
def fetch_staff():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM staff_members ORDER BY name").fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Adds a new staff member by auto-generating an employee ID and inserting their details into the database.
def add_staff(data):
    conn = get_connection()

    last_row = conn.execute("""
        SELECT employee_id FROM staff_members
        ORDER BY employee_id DESC LIMIT 1
    """).fetchone()

    next_number = 100
    if last_row:
        try:
            next_number = int(last_row["employee_id"].split("-")[1]) + 1
        except Exception:
            next_number = 100

    employee_id = f"EMP-{next_number:04d}"

    conn.execute("""
        INSERT INTO staff_members (employee_id, name, department, role, status, last_login)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        employee_id,
        data.get("name", ""),
        data.get("department", ""),
        data.get("role", ""),
        "Active",
        "Never"
    ))

    conn.commit()
    conn.close()
    return {"success": True}


# Updates the role of an existing staff member identified by their employee ID.
def edit_staff_role(data):
    conn = get_connection()
    conn.execute("""
        UPDATE staff_members
        SET role = ?
        WHERE employee_id = ?
    """, (
        data.get("role", ""),
        data.get("employeeId", "")
    ))
    conn.commit()
    conn.close()
    return {"success": True}


# Toggles a staff member's status between "Active" and "Inactive" based on their current status.
def toggle_staff_status(data):
    conn = get_connection()
    member = conn.execute("""
        SELECT status FROM staff_members WHERE employee_id = ?
    """, (data.get("employeeId", ""),)).fetchone()

    if not member:
        conn.close()
        return {"success": False, "message": "Staff member not found."}

    new_status = "Inactive" if member["status"] == "Active" else "Active"

    conn.execute("""
        UPDATE staff_members
        SET status = ?
        WHERE employee_id = ?
    """, (new_status, data.get("employeeId", "")))

    conn.commit()
    conn.close()
    return {"success": True}