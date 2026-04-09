from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

rfid_items = {
    "103701245": {
        "name": "Bohrmaschine",
        "image": "boormachine.jpg",
        "description": "Elektrische Bohrmaschine",
        "start_date": "2026-04-01",
        "end_date": "2026-04-07"
    },
    "91141454": {
        "name": "UNO",
        "image": "uno.jpg",
        "description": "Kartenspiel",
        "start_date": "2026-04-02",
        "end_date": "2026-04-09"
    }
}

@app.route('/')
def index():
    return render_template('scanner.html')

@app.route("/item/<tag_id>")
def item(tag_id):
    item = rfid_items.get(tag_id)
    if not item:
        return "Item niet gevonden"
    return render_template("item.html", item=item)

@app.route('/scan/<tag_id>')
def scan(tag_id):
    if tag_id not in rfid_items:
        return {"error": "Item niet gevonden"}, 404

    socketio.emit('new_scan', {'tag_id': tag_id})
    return {"status": "success", "redirect_url": f"/item/{tag_id}"}

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)