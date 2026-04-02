from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

EXPECTED_WEIGHT = 500
TOLERANCE = 20

@app.route("/")
def index():
    return render_template("index.html", expected=EXPECTED_WEIGHT)

@app.route("/weight")
def weight():
    actual = random.randint(450, 550)

    if abs(actual - EXPECTED_WEIGHT) <= TOLERANCE:
        return jsonify({
            "status": "correct",
            "message": "Item correct geplaatst",
            "actual": actual
        })
    else:
        return jsonify({
            "status": "wrong",
            "message": "Verkeerd item",
            "actual": actual
        })

app.run(debug=True)