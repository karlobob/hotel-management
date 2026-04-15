import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs

# Import database and modules
from database import init_db
from housekeeping import fetch_all_rooms, fetch_housekeepers, update_room
from loyalty import (
    fetch_loyalty_members,
    fetch_rewards,
    lookup_member,
    redeem_reward,
    add_points_manually
)
from staff import fetch_staff, add_staff, edit_staff_role, toggle_staff_status
from guest_registration import get_guest_meta, create_guest

PORT = 8000


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

        # Serve HTML pages
        if parsed.path == "/":
            self.path = "/templates/housekeeping.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        if parsed.path == "/loyalty":
            self.path = "/templates/loyalty.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        if parsed.path == "/staff":
            self.path = "/templates/staff.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        if parsed.path == "/guest-registration":
            self.path = "/templates/guest_registration.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        # API: Get all data for frontend
        if parsed.path == "/api/data":
            self.send_json(get_all_data())
            return

        # API: Guest registration meta
        if parsed.path == "/api/guest-registration/meta":
            self.send_json(get_guest_meta())
            return

        # API: Loyalty member lookup
        if parsed.path == "/api/loyalty/member":
            params = parse_qs(parsed.query)
            lookup_value = params.get("lookup", [""])[0]
            last_name = params.get("lastName", [""])[0]
            self.send_json(lookup_member(lookup_value, last_name))
            return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        parsed = urlparse(self.path)

        # Housekeeping: Update room
        if parsed.path == "/api/rooms/update":
            data = read_json_body(self)
            self.send_json(update_room(data))
            return

        # Loyalty: Redeem reward
        if parsed.path == "/api/loyalty/redeem":
            data = read_json_body(self)
            result = redeem_reward(data)
            status = 200 if result.get("success") else 400
            self.send_json(result, status=status)
            return

        # Loyalty: Add points manually
        if parsed.path == "/api/loyalty/add-points":
            data = read_json_body(self)
            result = add_points_manually(data)
            status = 200 if result.get("success") else 400
            self.send_json(result, status=status)
            return

        # Staff: Add new staff
        if parsed.path == "/api/staff/add":
            data = read_json_body(self)
            self.send_json(add_staff(data))
            return

        # Staff: Edit role
        if parsed.path == "/api/staff/edit-role":
            data = read_json_body(self)
            self.send_json(edit_staff_role(data))
            return

        # Staff: Toggle status
        if parsed.path == "/api/staff/toggle-status":
            data = read_json_body(self)
            result = toggle_staff_status(data)
            status = 200 if result.get("success") else 400
            self.send_json(result, status=status)
            return

        # Guest registration: Create account
        if parsed.path == "/api/guest-registration/create":
            data = read_json_body(self)
            self.send_json(create_guest(data))
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