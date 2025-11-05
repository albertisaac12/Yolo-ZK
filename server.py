from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/face-data", methods=["POST"])
def receive_face():
    data = request.get_json()

    # TODO: run your proof verification here
    verified = True  # dummy result

    if verified:
        return jsonify({"status": "verified"}), 200
    else:
        return jsonify({"status": "rejected"}), 401

if __name__ == "__main__":
    app.run(port=5000, debug=True)
