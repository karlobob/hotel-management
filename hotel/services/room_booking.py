# room_booking.py
# This file contains functions for room booking.
# It handles:
# 1. creating auto-generated reservation information
# 2. counting rooms available
# 3. saving a booking into SQLite

#from database import get_connection
from hotel.services.database import get_connection
from datetime import datetime


def generate_reservation_id():
    """
    Generate a simple reservation ID like RES-1001, RES-1002, etc.
    It checks how many reservations already exist in the database.
    """
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS count FROM reservations").fetchone()
    conn.close()
    next_number = row["count"] + 1001
    return f"RES-{next_number}"


def get_created_at():
    """
    Return the current date in a readable format.
    Example: April 25, 2026
    """
    return datetime.now().strftime("%B %d, %Y")


def count_available_rooms(room_type):
    """
    Count how many rooms exist in the rooms table for the selected room type.
    This is a simple version and does not yet check booking overlap by date.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) AS count FROM rooms WHERE type = ?",
        (room_type,)
    ).fetchone()
    conn.close()
    return row["count"]


def get_booking_meta():
    """
    Return auto-generated reservation data for the booking form.
    """
    return {
        "reservationId": generate_reservation_id(),
        "createdAt": get_created_at()
    }


def get_available_rooms(data):
    """
    Return how many rooms are available based on selected room type.
    This simple version counts rooms by type only.
    """
    room_type = data.get("roomType", "")
    available = count_available_rooms(room_type)

    return {
        "success": True,
        "availableRooms": available
    }


def create_reservation(data):
    """
    Save a room reservation into the reservations table.
    """
    reservation_id = generate_reservation_id()
    created_at = get_created_at()

    conn = get_connection()
    conn.execute("""
        INSERT INTO reservations (
            reservation_id,
            guest_id,
            number_of_guests,
            check_in_date,
            check_out_date,
            room_type,
            rate_per_night,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reservation_id,
        data.get("guestId", ""),
        data.get("numberOfGuests", ""),
        data.get("checkInDate", ""),
        data.get("checkOutDate", ""),
        data.get("roomType", ""),
        data.get("ratePerNight", 0),
        data.get("status", "Pending"),
        created_at
    ))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "reservationId": reservation_id,
        "createdAt": created_at
    }