from flask import Flask, request, jsonify, render_template, url_for, redirect

app = Flask(__name__)

rfid_items = {
    "103701245": {"name":"Bohrmaschine","image":"bohrmaschine.jpg","description":"Elektrische Bohrmaschine","start_date":"2026-04-01","end_date":"2026-04-07"},
    "91141454": {"name":"UNO","image":"uno.jpg","description":"Kartenspiel","start_date":"2026-04-02","end_date":"2026-04-09"}
}

last_scan = None

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    if not data or "tag" not in data:
        return jsonify({"error": "Geen tag ontvangen"}), 400
    
    tag_id = str(data["tag"])
    if tag_id not in rfid_items:
        return jsonify({"error": "Item niet gevonden"}), 404
    
    return redirect(f"/item/{tag_id}")

@app.route("/item/<tag_id>")
def item(tag_id):
    item = rfid_items.get(tag_id)
    if not item:
        return "Item niet gevonden"
    return render_template("item.html", item=item)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)