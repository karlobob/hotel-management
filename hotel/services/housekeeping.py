#from database import get_connection
from hotel.services.database import get_connection


# Retrieves all rooms from the database, ordered by room number, and returns them as a list of dictionaries.
def fetch_all_rooms():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rooms ORDER BY number").fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Retrieves all housekeeper names from the database, ordered alphabetically,
# and returns them as a list of strings.
def fetch_housekeepers():
    conn = get_connection()
    rows = conn.execute("SELECT name FROM housekeepers ORDER BY name").fetchall()
    conn.close()
    return [row["name"] for row in rows]


# Updates a room's status, assigned housekeeper, priority, and notes based on the provided data dictionary.
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