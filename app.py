from flask import Flask, render_template
from flask_socketio import SocketIO
from models import db, Items

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///items.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('scanner.html')

@app.route("/item/<tag_id>")
def item(tag_id):
    item = Items.query.filter_by(rfid=int(tag_id)).first()

    if not item:
        return "Item niet gevonden"

    return render_template("item.html", item=item)

@app.route('/scan/<tag_id>')
def scan(tag_id):
    item = Items.query.filter_by(rfid=int(tag_id)).first()

    if not item:
        return {"error": "Item niet gevonden"}, 404

    socketio.emit('new_scan', {'tag_id': tag_id})
    return {"status": "success", "redirect_url": f"/item/{tag_id}"}

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)