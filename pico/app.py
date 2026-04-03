from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/temperature", methods=["POST"])
def temperature():
    data = request.json  
    card = data["RFID-tag"]
    
    print("RFID:", card)
   
    return jsonify({"RFID-tag": card})



app.run(host="0.0.0.0", port=5000, debug=True)