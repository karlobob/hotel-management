import http.server
import socketserver
import os
import json
import sqlite3
from urllib.parse import urlparse, parse_qs

PORT = 8000
DB_NAME = "hotel.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


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

    conn.commit()

    seed_data(conn)
    conn.close()


def seed_data(conn):
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS count FROM rooms")
    if cur.fetchone()["count"] == 0:
        cur.executemany("""
            INSERT INTO rooms (number, type, status, priority, housekeeper, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("201", "Standard", "Clean", "Standard", "", ""),
            ("202", "Standard", "Dirty", "Standard", "", ""),
            ("203", "Deluxe", "Occupied", "Standard", "", ""),
            ("204", "Deluxe", "In Progress", "Standard", "", "")
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

        cur.executemany("""
            INSERT INTO loyalty_activity (
                member_id, date, description, ref_id, points, balance, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            ("G-10042", "Mar 18 2026", "Room stay – Executive Suite (3 nights)", "RES-20481", 2400, 14850, ""),
            ("G-10042", "Feb 02 2026", "Reward Redemption - Complimentary Breakfast", "RDM-00992", -500, 12450, ""),
            ("G-10042", "Jan 14 2026", "Room stay – Deluxe Double (2 nights)", "RES-19844", 1200, 12950, ""),
            ("G-10042", "Dec 27 2025", "Bonus points – Holiday promotion", "PROMO-HOL25", 1000, 11750, ""),
            ("G-10042", "Nov 08 2025", "Room stay – Standard Single (1 night)", "RES-18720", 600, 10750, "")
        ])

    cur.execute("SELECT COUNT(*) AS count FROM rewards")
    if cur.fetchone()["count"] == 0:
        cur.executemany("""
            INSERT INTO rewards (id, title, points, description)
            VALUES (?, ?, ?, ?)
        """, [
            ("reward-1", "Complimentary Breakfast", 500, "Full buffet breakfast for 1 guest"),
            ("reward-2", "Room Upgrade", 2000, "Upgrade to next available room tier"),
            ("reward-3", "Spa Access – Full Day", 3500, "Full-day access for 1 guest"),
            ("reward-4", "Late Check-Out (2 PM)", 750, "Guaranteed 2:00 PM check-out"),
            ("reward-5", "Airport Transfer", 1500, "One-way private car to/from airport"),
            ("reward-6", "Free Night Stay", 8000, "1 complimentary night (standard room)")
        ])

    cur.execute("SELECT COUNT(*) AS count FROM staff_members")
    if cur.fetchone()["count"] == 0:
        cur.executemany("""
            INSERT INTO staff_members (employee_id, name, department, role, status, last_login)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("EMP-0012", "Amanda Lewis", "Management", "Administrator", "Active", "Today, 09:14"),
            ("EMP-0031", "Robert Kim", "Front Desk", "Manager", "Active", "Today, 08:42"),
            ("EMP-0058", "Maria Santos", "Housekeeping", "Housekeeper", "Active", "Today, 07:58"),
            ("EMP-0074", "Priya Desai", "Front Desk", "Front Desk Agent", "Active", "Yesterday, 16:30"),
            ("EMP-0085", "James Okafor", "Housekeeping", "Housekeeper", "Active", "Today, 06:15"),
            ("EMP-0093", "Thomas Cruz", "Maintenance", "Maintenance", "Inactive", "Mar 10, 2026")
        ])

    conn.commit()


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


def fetch_rewards():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rewards ORDER BY title").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def fetch_staff():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM staff_members ORDER BY name").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def fetch_loyalty_members():
    conn = get_connection()
    members = conn.execute("SELECT * FROM loyalty_members ORDER BY full_name").fetchall()
    result = []

    for member in members:
        activity = conn.execute("""
            SELECT date, description, ref_id, points, balance, notes
            FROM loyalty_activity
            WHERE member_id = ?
            ORDER BY id DESC
        """, (member["id"],)).fetchall()

        result.append({
            "id": member["id"],
            "email": member["email"],
            "lastName": member["last_name"],
            "firstName": member["first_name"],
            "fullName": member["full_name"],
            "tier": member["tier"],
            "enrolled": member["enrolled"],
            "availablePoints": member["available_points"],
            "lifetimeStays": member["lifetime_stays"],
            "nightsThisYear": member["nights_this_year"],
            "nextTier": member["next_tier"],
            "nextTierPoints": member["next_tier_points"],
            "activityHistory": [
                {
                    "date": a["date"],
                    "description": a["description"],
                    "refId": a["ref_id"],
                    "points": a["points"],
                    "balance": a["balance"],
                    "notes": a["notes"]
                } for a in activity
            ]
        })

    conn.close()
    return result


def get_all_data():
    return {
        "rooms": fetch_all_rooms(),
        "housekeepers": fetch_housekeepers(),
        "loyaltyMembers": fetch_loyalty_members(),
        "rewards": fetch_rewards(),
        "staffMembers": fetch_staff()
    }


def read_json_body(handler):
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")
    return json.loads(body) if body else {}


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.path = "/templates/index.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        if parsed.path == "/loyalty":
            self.path = "/templates/loyalty.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        if parsed.path == "/staff":
            self.path = "/templates/staff.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        if parsed.path == "/api/data":
            self.send_json(get_all_data())
            return

        if parsed.path == "/api/loyalty/member":
            params = parse_qs(parsed.query)
            member_id_or_email = params.get("lookup", [""])[0].strip().lower()
            last_name = params.get("lastName", [""])[0].strip().lower()

            members = fetch_loyalty_members()
            member = next(
                (
                    m for m in members
                    if (m["id"].lower() == member_id_or_email or m["email"].lower() == member_id_or_email)
                    and m["lastName"].lower() == last_name
                ),
                None
            )
            self.send_json({"member": member})
            return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/rooms/update":
            data = read_json_body(self)
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
            self.send_json({"success": True})
            return

        if parsed.path == "/api/loyalty/redeem":
            data = read_json_body(self)
            member_id = data.get("memberId", "")
            reward_id = data.get("rewardId", "")
            reservation_id = data.get("reservationId", "") or "RDM-MANUAL"
            notes = data.get("notes", "")

            conn = get_connection()
            member = conn.execute("SELECT * FROM loyalty_members WHERE id = ?", (member_id,)).fetchone()
            reward = conn.execute("SELECT * FROM rewards WHERE id = ?", (reward_id,)).fetchone()

            if not member or not reward:
                conn.close()
                self.send_json({"success": False, "message": "Member or reward not found."}, status=400)
                return

            if member["available_points"] < reward["points"]:
                conn.close()
                self.send_json({"success": False, "message": "Not enough points."}, status=400)
                return

            new_balance = member["available_points"] - reward["points"]

            conn.execute("""
                UPDATE loyalty_members
                SET available_points = ?
                WHERE id = ?
            """, (new_balance, member_id))

            conn.execute("""
                INSERT INTO loyalty_activity (member_id, date, description, ref_id, points, balance, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                member_id,
                data.get("date", ""),
                f"Reward Redemption - {reward['title']}",
                reservation_id,
                -reward["points"],
                new_balance,
                notes
            ))

            conn.commit()
            conn.close()
            self.send_json({"success": True})
            return

        if parsed.path == "/api/loyalty/add-points":
            data = read_json_body(self)
            member_id = data.get("memberId", "")
            points_to_add = int(data.get("points", 0))

            conn = get_connection()
            member = conn.execute("SELECT * FROM loyalty_members WHERE id = ?", (member_id,)).fetchone()

            if not member:
                conn.close()
                self.send_json({"success": False, "message": "Member not found."}, status=400)
                return

            new_balance = member["available_points"] + points_to_add

            conn.execute("""
                UPDATE loyalty_members
                SET available_points = ?
                WHERE id = ?
            """, (new_balance, member_id))

            conn.execute("""
                INSERT INTO loyalty_activity (member_id, date, description, ref_id, points, balance, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                member_id,
                data.get("date", ""),
                "Manual points adjustment",
                "MANUAL-ADD",
                points_to_add,
                new_balance,
                ""
            ))

            conn.commit()
            conn.close()
            self.send_json({"success": True})
            return

        if parsed.path == "/api/staff/add":
            data = read_json_body(self)
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
            self.send_json({"success": True})
            return

        if parsed.path == "/api/staff/edit-role":
            data = read_json_body(self)
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
            self.send_json({"success": True})
            return

        if parsed.path == "/api/staff/toggle-status":
            data = read_json_body(self)
            conn = get_connection()
            member = conn.execute("""
                SELECT status FROM staff_members WHERE employee_id = ?
            """, (data.get("employeeId", ""),)).fetchone()

            if not member:
                conn.close()
                self.send_json({"success": False, "message": "Staff member not found."}, status=400)
                return

            new_status = "Inactive" if member["status"] == "Active" else "Active"

            conn.execute("""
                UPDATE staff_members
                SET status = ?
                WHERE employee_id = ?
            """, (new_status, data.get("employeeId", "")))

            conn.commit()
            conn.close()
            self.send_json({"success": True})
            return

        self.send_json({"success": False, "message": "Unknown endpoint."}, status=404)

    def send_json(self, data, status=200):
        response = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(response)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_db()
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()