from database import get_connection


def fetch_all_rooms():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rooms ORDER BY number").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def fetch_housekeepers():
    conn = get_connection()
    rows = conn.execute("SELECT name FROM housekeepers ORDER BY name").fetchall()
    conn.close()
    return [row["name"] for row in rows]


def update_room(data):
    conn = get_connection()
    conn.execute("""
        UPDATE rooms
        SET status = ?, housekeeper = ?, priority = ?, notes = ?
        WHERE number = ?
    """, (
        data.get("status", ""),
        data.get("housekeeper", ""),
        data.get("priority", "Standard"),
        data.get("notes", ""),
        data.get("number", "")
    ))
    conn.commit()
    conn.close()
    return {"success": True}