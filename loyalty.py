from database import get_connection


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


def fetch_rewards():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rewards ORDER BY title").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def lookup_member(lookup_value, last_name):
    members = fetch_loyalty_members()
    lookup_lower = lookup_value.strip().lower()
    last_name_lower = last_name.strip().lower()

    member = next(
        (
            m for m in members
            if (m["id"].lower() == lookup_lower or m["email"].lower() == lookup_lower)
            and m["lastName"].lower() == last_name_lower
        ),
        None
    )
    return {"member": member}


def redeem_reward(data):
    member_id = data.get("memberId", "")
    reward_id = data.get("rewardId", "")
    reservation_id = data.get("reservationId", "") or "RDM-MANUAL"
    notes = data.get("notes", "")

    conn = get_connection()
    member = conn.execute("SELECT * FROM loyalty_members WHERE id = ?", (member_id,)).fetchone()
    reward = conn.execute("SELECT * FROM rewards WHERE id = ?", (reward_id,)).fetchone()

    if not member or not reward:
        conn.close()
        return {"success": False, "message": "Member or reward not found."}

    if member["available_points"] < reward["points"]:
        conn.close()
        return {"success": False, "message": "Not enough points."}

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
    return {"success": True}


def add_points_manually(data):
    member_id = data.get("memberId", "")
    points_to_add = int(data.get("points", 0))

    conn = get_connection()
    member = conn.execute("SELECT * FROM loyalty_members WHERE id = ?", (member_id,)).fetchone()

    if not member:
        conn.close()
        return {"success": False, "message": "Member not found."}

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
    return {"success": True}