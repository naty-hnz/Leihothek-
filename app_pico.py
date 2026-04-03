from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/temperature", methods=["POST"])
def temperature():
    data = request.json  
    temp = data["temperature"]
    
    print("temp ontvangen:", temp)
   
    if temp > 20:
        return jsonify({"warning": True})
    else:
        return jsonify({"warning": False})



app.run(host="0.0.0.0", port=5000, debug=True)
