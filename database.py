import sqlite3
from datetime import datetime

DB_NAME = "hotel.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def get_today_member_since():
    return datetime.now().strftime("%B %Y")


def generate_guest_id():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS count FROM guests").fetchone()
    conn.close()
    next_number = row["count"] + 1001
    return f"G-{next_number}"


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            number TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            housekeeper TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS housekeepers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS loyalty_members (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            full_name TEXT NOT NULL,
            tier TEXT NOT NULL,
            enrolled TEXT NOT NULL,
            available_points INTEGER NOT NULL,
            lifetime_stays INTEGER NOT NULL,
            nights_this_year INTEGER NOT NULL,
            next_tier TEXT NOT NULL,
            next_tier_points INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS loyalty_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            ref_id TEXT NOT NULL,
            points INTEGER NOT NULL,
            balance INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY(member_id) REFERENCES loyalty_members(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rewards (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            points INTEGER NOT NULL,
            description TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS staff_members (
            employee_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            last_login TEXT NOT NULL
        )
    """)

    # Guest Registration table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            guest_id TEXT PRIMARY KEY,
            member_since TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone_number TEXT,
            date_of_birth TEXT,
            passport_id TEXT,
            high_floor INTEGER DEFAULT 0,
            quiet_room INTEGER DEFAULT 0,
            feather_free_pillows INTEGER DEFAULT 0,
            accessible_room INTEGER DEFAULT 0,
            king_bed INTEGER DEFAULT 0,
            preference_notes TEXT
        )
    """)

    # Reservations table
    # This stores room bookings and check-in/check-out info
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            reservation_id TEXT PRIMARY KEY,
            guest_id TEXT NOT NULL,
            number_of_guests INTEGER NOT NULL,
            check_in_date TEXT NOT NULL,
            check_out_date TEXT NOT NULL,
            room_type TEXT NOT NULL,
            rate_per_night REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            room_id TEXT
        )
    """)

    conn.commit()
    seed_data(conn)
    conn.close()


def seed_data(conn):
    cur = conn.cursor()

    cur.execute("DELETE FROM rooms")
    cur.executemany("""
        INSERT INTO rooms (number, type, status, priority, housekeeper, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ("101", "Standard", "Clean", "Standard", "", ""),
        ("102", "Standard", "Dirty", "Standard", "", ""),
        ("103", "Deluxe", "Occupied", "Standard", "", ""),
        ("104", "Deluxe", "In Progress", "Standard", "", ""),
        ("105", "Suite", "Clean", "Standard", "", "")
    ])

    cur.execute("SELECT COUNT(*) AS count FROM housekeepers")
    if cur.fetchone()["count"] == 0:
        cur.executemany("INSERT INTO housekeepers (name) VALUES (?)", [
            ("Emma Johnson",),
            ("Liam Smith",),
            ("Olivia Brown",),
            ("Noah Davis",)
        ])

    cur.execute("SELECT COUNT(*) AS count FROM loyalty_members")
    if cur.fetchone()["count"] == 0:
        cur.execute("""
            INSERT INTO loyalty_members (
                id, email, last_name, first_name, full_name, tier, enrolled,
                available_points, lifetime_stays, nights_this_year, next_tier, next_tier_points
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "G-10042",
            "james.thornton@email.com",
            "Thornton",
            "James",
            "James Thornton",
            "Gold Member",
            "March 2021",
            14850,
            23,
            18,
            "Platinum",
            20000
        ))

    cur.execute("SELECT COUNT(*) AS count FROM rewards")
    if cur.fetchone()["count"] == 0:
        cur.executemany("""
            INSERT INTO rewards (id, title, points, description)
            VALUES (?, ?, ?, ?)
        """, [
            ("reward-1", "Complimentary Breakfast", 500, "Full buffet breakfast for 1 guest"),
            ("reward-2", "Room Upgrade", 2000, "Upgrade to next available room tier"),
            ("reward-3", "Spa Access – Full Day", 3500, "Full-day access for 1 guest")
        ])

    cur.execute("SELECT COUNT(*) AS count FROM staff_members")
    if cur.fetchone()["count"] == 0:
        cur.executemany("""
            INSERT INTO staff_members (employee_id, name, department, role, status, last_login)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("EMP-0012", "Amanda Lewis", "Management", "Administrator", "Active", "Today, 09:14"),
            ("EMP-0031", "Robert Kim", "Front Desk", "Manager", "Active", "Today, 08:42")
        ])

    conn.commit()