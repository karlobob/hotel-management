from database import get_connection, get_today_member_since, generate_guest_id


def get_guest_meta():
    return {
        "guestId": generate_guest_id(),
        "memberSince": get_today_member_since()
    }


def create_guest(data):
    guest_id = generate_guest_id()
    member_since = get_today_member_since()

    conn = get_connection()
    conn.execute("""
        INSERT INTO guests (
            guest_id, member_since, first_name, last_name, email, phone_number,
            date_of_birth, passport_id, high_floor, quiet_room, feather_free_pillows,
            accessible_room, king_bed, preference_notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        guest_id,
        member_since,
        data.get("firstName", ""),
        data.get("lastName", ""),
        data.get("email", ""),
        data.get("phoneNumber", ""),
        data.get("dateOfBirth", ""),
        data.get("passportId", ""),
        1 if data.get("highFloor") else 0,
        1 if data.get("quietRoom") else 0,
        1 if data.get("featherFreePillows") else 0,
        1 if data.get("accessibleRoom") else 0,
        1 if data.get("kingBed") else 0,
        data.get("preferenceNotes", "")
    ))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "guestId": guest_id,
        "memberSince": member_since
    }