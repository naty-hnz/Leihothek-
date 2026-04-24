from flask import Flask, jsonify, render_template, request
import database as db
import locker as lk

app = Flask(__name__)

# ─── Pico W endpoints ─────────────────────────────────────────────────────────

@app.route("/api/weight_update", methods=["POST"])
def weight_update():
    lk.handle_weight_update(request.json.get("weight", 0.0))
    return jsonify({"ok": True})

@app.route("/api/locker_event", methods=["POST"])
def locker_event():
    data   = request.json
    event  = data.get("event")
    tag_id = str(data.get("tag_id", ""))
    weight = data.get("weight", 0.0)

    lk.update_live_weight(weight)

    if event == "rfid_scan":
        result = lk.handle_rfid_scan(tag_id, weight)
        return jsonify(result)

    return jsonify({"ok": True})

# ─── Admin UI endpoints ───────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def status():
    return jsonify(lk.get_full_status())

@app.route("/api/lockers")
def lockers():
    return jsonify(db.get_all_lockers())

@app.route("/api/lockers/add", methods=["POST"])
def add_locker():
    d = request.json
    try:
        db.add_locker(
            name        = d["name"],
            tag_id      = d.get("tag_id", ""),
            expected_g  = float(d.get("expected", 0)),
            tolerance_g = float(d.get("tolerance", 30)),
        )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/lockers/update", methods=["POST"])
def update_locker():
    d = request.json
    try:
        db.update_locker_fields(
            int(d["id"]),
            name        = d["name"],
            tag_id      = str(d["tag_id"]),
            expected_g  = float(d["expected"]),
            tolerance_g = float(d["tolerance"]),
        )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/lockers/delete", methods=["POST"])
def delete_locker():
    db.delete_locker(request.json["id"])
    return jsonify({"ok": True})

@app.route("/api/lockers/reset_status", methods=["POST"])
def reset_status():
    lk.reset_locker_status(request.json["id"])
    return jsonify({"ok": True})

@app.route("/api/events")
def events():
    return jsonify(db.get_events())

# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    db.init_db()
    print("Admin UI: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
