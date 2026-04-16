# checkin_checkout.py
# This file contains functions for Check-In and Check-Out operations.
# It handles:
# 1. Looking up reservations by reservation ID and guest ID
# 2. Processing check-in (assigning room, updating status)
# 3. Processing check-out (updating status, freeing room)
# 4. Counting available rooms

#from database import get_connection
from hotel.services.database import get_connection
from datetime import datetime


# This function retrieves the current date formatted as "YYYY-MM-DD".
# It is used to provide a default date value for check-in or check-out operations
# so that the system always references today's date when no specific date is given.
def get_today_date():
    """
    Return today's date in YYYY-MM-DD format.
    Used for default check-in/check-out dates.
    """
    return datetime.now().strftime("%Y-%m-%d")


# This function searches the database for a reservation matching the provided
# reservation ID and guest ID. It validates that both IDs are supplied, queries
# the reservations table, and returns the full reservation details (room type,
# dates, status, etc.) if a match is found, or an error message if not.
# It is used when a front-desk agent needs to pull up a guest's reservation
# before performing a check-in or check-out.
def lookup_reservation(data):
    """
    Look up a reservation by reservation_id and guest_id.
    Returns reservation details if found.
    """
    reservation_id = data.get("reservationId", "").strip()
    guest_id = data.get("guestId", "").strip()

    # Validate inputs
    if not reservation_id or not guest_id:
        return {
            "success": False,
            "message": "Please provide both Reservation ID and Guest ID."
        }

    conn = get_connection()

    # Query the reservations table
    row = conn.execute("""
        SELECT * FROM reservations
        WHERE reservation_id = ? AND guest_id = ?
    """, (reservation_id, guest_id)).fetchone()

    conn.close()

    # Check if reservation exists
    if not row:
        return {
            "success": False,
            "message": "Reservation not found. Please check the IDs."
        }

    # Return reservation data
    return {
        "success": True,
        "reservation": {
            "reservationId": row["reservation_id"],
            "guestId": row["guest_id"],
            "roomId": row["room_id"] if "room_id" in row.keys() else "",
            "roomType": row["room_type"],
            "checkInDate": row["check_in_date"],
            "checkOutDate": row["check_out_date"],
            "status": row["status"],
            "createdAt": row["created_at"]
        }
    }


# This function counts the number of rooms that are currently available
# (i.e., have a status of 'Clean') for a specified room type. It queries
# the rooms table and returns the integer count. It is used internally
# by other functions and by the UI to display real-time room availability.
def count_available_rooms_by_type(room_type):
    """
    Count how many rooms are available (status = 'Clean') for a room type.
    Returns the count.
    """
    conn = get_connection()

    row = conn.execute("""
        SELECT COUNT(*) AS count FROM rooms
        WHERE type = ? AND status = 'Clean'
    """, (room_type,)).fetchone()

    conn.close()

    return row["count"] if row else 0


# This function fetches a single available room number for a given room type.
# It looks for rooms with a status of 'Clean' and returns the first match.
# If no rooms are available, it returns None. This is called during the
# check-in process to determine which specific room to assign to the guest.
def get_available_room(room_type):
    """
    Get one available room number for the specified room type.
    Returns the room number or None if no room is available.
    """
    conn = get_connection()

    row = conn.execute("""
        SELECT number FROM rooms
        WHERE type = ? AND status = 'Clean'
        LIMIT 1
    """, (room_type,)).fetchone()

    conn.close()

    return row["number"] if row else None


# This function handles the full check-in workflow for a guest. It validates
# the required reservation and guest IDs, finds an available room of the
# requested type using get_available_room(), then performs two database updates:
# it assigns the room to the reservation and sets its status to 'Checked-In',
# and it marks the room's status as 'Occupied'. On success it returns the
# assigned room number; on failure (missing IDs or no available rooms) it
# returns an appropriate error message.
def process_checkin(data):
    """
    Process guest check-in:
    1. Find an available room of the correct type
    2. Assign the room to the reservation
    3. Update reservation status to 'Checked-In'
    4. Update room status to 'Occupied'
    """
    reservation_id = data.get("reservationId", "").strip()
    guest_id = data.get("guestId", "").strip()
    room_type = data.get("roomType", "").strip()

    # Validate inputs
    if not reservation_id or not guest_id:
        return {
            "success": False,
            "message": "Reservation ID and Guest ID are required."
        }

    # Find an available room
    room_number = get_available_room(room_type)

    if not room_number:
        return {
            "success": False,
            "message": f"No available rooms of type '{room_type}'."
        }

    conn = get_connection()

    # Update the reservation with room assignment and status
    conn.execute("""
        UPDATE reservations
        SET room_id = ?, status = 'Checked-In'
        WHERE reservation_id = ? AND guest_id = ?
    """, (room_number, reservation_id, guest_id))

    # Update the room status to Occupied
    conn.execute("""
        UPDATE rooms
        SET status = 'Occupied'
        WHERE number = ?
    """, (room_number,))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Check-in completed. Room {room_number} assigned.",
        "roomId": room_number
    }


# This function handles the full check-out workflow for a guest. It validates
# the required reservation and guest IDs, then updates the reservation's status
# to 'Checked-Out'. If a room was assigned to the reservation, it also sets
# that room's status to 'Dirty' to signal that housekeeping is needed before
# the room can be made available again. It returns a success or error message.
def process_checkout(data):
    """
    Process guest check-out:
    1. Update reservation status to 'Checked-Out'
    2. Update room status to 'Dirty' (needs cleaning)
    """
    reservation_id = data.get("reservationId", "").strip()
    guest_id = data.get("guestId", "").strip()
    room_id = data.get("roomId", "").strip()

    # Validate inputs
    if not reservation_id or not guest_id:
        return {
            "success": False,
            "message": "Reservation ID and Guest ID are required."
        }

    conn = get_connection()

    # Update reservation status to Checked-Out
    conn.execute("""
        UPDATE reservations
        SET status = 'Checked-Out'
        WHERE reservation_id = ? AND guest_id = ?
    """, (reservation_id, guest_id))

    # Update room status to Dirty if room was assigned
    if room_id:
        conn.execute("""
            UPDATE rooms
            SET status = 'Dirty'
            WHERE number = ?
        """, (room_id,))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Check-out completed successfully."
    }


# This function serves as an API-facing wrapper around count_available_rooms_by_type().
# It extracts the room type from the incoming request data, calls the counting
# function, and returns the result in a standardized response dictionary.
# It is used by the front-end form to display how many rooms of a particular
# type are still available for assignment.
def get_rooms_available_count(data):
    """
    Return count of available rooms for a given room type.
    Used to display availability on the form.
    """
    room_type = data.get("roomType", "")

    count = count_available_rooms_by_type(room_type)

    return {
        "success": True,
        "availableRooms": count
    }