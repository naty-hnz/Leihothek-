from flask import Flask, jsonify, render_template, request
import sqlite3
import serial
import serial.tools.list_ports
import threading
import time

app = Flask(__name__)
DB_FILE = "scale_data.db"

state = {
    "weight": 0.0,
    "connected": False,
    "port": None,
    "error": None,
}
serial_reader = None

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        expected_weight_g REAL,
        tolerance_g REAL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        product TEXT,
        expected_g REAL,
        measured_g REAL,
        match INTEGER
    )''')
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, expected_weight_g, tolerance_g FROM products ORDER BY name")
    rows = [{"name": r[0], "expected": r[1], "tolerance": r[2]} for r in c.fetchall()]
    conn.close()
    return rows

def get_measurements(limit=50):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""SELECT timestamp, product, expected_g, measured_g, match
                 FROM measurements ORDER BY id DESC LIMIT ?""", (limit,))
    rows = [{"time": r[0], "product": r[1], "expected": r[2],
             "measured": r[3], "match": bool(r[4])} for r in c.fetchall()]
    conn.close()
    return rows

def save_measurement(product, expected, measured, match):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT INTO measurements (timestamp, product, expected_g, measured_g, match)
                 VALUES (datetime('now','localtime'), ?, ?, ?, ?)''',
              (product, expected, measured, 1 if match else 0))
    conn.commit()
    conn.close()

class SerialReader(threading.Thread):
    def __init__(self, port):
        super().__init__(daemon=True)
        self.port = port
        self.running = True

    def run(self):
        try:
            ser = serial.Serial(self.port, 115200, timeout=2)
            state["connected"] = True
            state["error"] = None
            while self.running:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line.startswith("Weight:"):
                    try:
                        state["weight"] = float(
                            line.replace("Weight:", "").replace("g", "").strip()
                        )
                    except ValueError:
                        pass
            ser.close()
        except Exception as e:
            state["connected"] = False
            state["error"] = str(e)

    def stop(self):
        self.running = False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def status():
    return jsonify({
        "weight": round(state["weight"], 1),
        "connected": state["connected"],
        "error": state["error"],
    })

@app.route("/api/products")
def products():
    return jsonify(get_products())

@app.route("/api/products/add", methods=["POST"])
def add_product():
    data = request.json
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO products (name, expected_weight_g, tolerance_g)
                     VALUES (?, ?, ?)''',
                  (data["name"], float(data["expected"]), float(data["tolerance"])))
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/products/delete", methods=["POST"])
def delete_product():
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE name = ?", (data["name"],))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/measurements")
def measurements():
    return jsonify(get_measurements())

@app.route("/api/ports")
def ports():
    return jsonify([p.device for p in serial.tools.list_ports.comports()])

@app.route("/api/connect", methods=["POST"])
def connect():
    global serial_reader
    port = request.json.get("port")
    if serial_reader and serial_reader.running:
        serial_reader.stop()
        time.sleep(0.5)
    state["port"] = port
    state["connected"] = False
    serial_reader = SerialReader(port)
    serial_reader.start()
    time.sleep(1)
    return jsonify({"ok": True, "connected": state["connected"], "error": state["error"]})

@app.route("/api/disconnect", methods=["POST"])
def disconnect():
    global serial_reader
    if serial_reader:
        serial_reader.stop()
        serial_reader = None
    state["connected"] = False
    return jsonify({"ok": True})

@app.route("/api/log", methods=["POST"])
def log():
    data = request.json
    save_measurement(data["product"], data["expected"], data["measured"], data["match"])
    return jsonify({"ok": True})

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
