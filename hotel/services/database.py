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
    conn.close()