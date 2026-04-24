import time
import database as db

# ─── Statuses ────────────────────────────────────────────────────────────────
CLOSED           = "CLOSED"
OPEN             = "OPEN"
SUCCESS_RETURNED = "SUCCESS_RETURNED"
FAILED_RETURN    = "FAILED_RETURN"

# ─── Live state (in-memory, updated by Pico W) ───────────────────────────────
live = {
    "weight":      0.0,
    "last_tag":    None,
    "last_update": None,
}

def update_live_weight(weight):
    live["weight"]      = weight
    live["last_update"] = time.strftime("%H:%M:%S")

# ─── State machine ───────────────────────────────────────────────────────────

def handle_rfid_scan(tag_id, weight):
    """
    Called when the Pico W scans an RFID tag.
    Returns a dict with 'action' and optional 'expected' for the Pico to act on.
    """
    live["last_tag"]    = tag_id
    live["last_update"] = time.strftime("%H:%M:%S")

    locker = db.get_locker_by_tag(tag_id)

    if not locker:
        db.log_event(None, "rfid_scan", tag_id=tag_id, weight=weight, result="unknown_tag")
        return {"action": "unknown_tag"}

    status    = locker["status"]
    expected  = locker["expected"]
    tolerance = locker["tolerance"]
    diff      = abs(weight - expected)

    # Item is in locker — user wants to take it out
    if status in (CLOSED, SUCCESS_RETURNED):
        db.update_locker_fields(locker["id"], status=OPEN, current_g=weight)
        db.log_event(locker["name"], "checkout", tag_id=tag_id, weight=weight, result="opened_checkout")
        return {"action": "open_checkout"}

    # Locker is open — user is returning the item
    if status in (OPEN, FAILED_RETURN):
        if diff <= tolerance:
            db.update_locker_fields(locker["id"], status=SUCCESS_RETURNED, current_g=weight)
            db.log_event(locker["name"], "return", tag_id=tag_id, weight=weight,
                         expected=expected, result="success_returned")
            return {"action": "open_return_ok", "expected": expected}
        else:
            db.update_locker_fields(locker["id"], status=FAILED_RETURN, current_g=weight)
            db.log_event(locker["name"], "return", tag_id=tag_id, weight=weight,
                         expected=expected, result="failed_return")
            return {"action": "return_wrong_weight", "expected": expected}

    return {"action": "denied"}


def handle_weight_update(weight):
    """Called every second by the Pico W to push the latest weight."""
    update_live_weight(weight)


def reset_locker_status(locker_id):
    """Admin manually resets a locker back to CLOSED."""
    db.update_locker_fields(locker_id, status=CLOSED)


def get_full_status():
    """Returns live state + all locker data for the admin UI."""
    return {**live, "lockers": db.get_all_lockers()}
