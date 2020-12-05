from flask import Flask, jsonify, request
from server import Server

app = Flask(__name__)
server = Server()

@app.route('/request/issue-key', methods=['POST'])
def issue_key():
    req = request.get_json()
    response = server.issue_key(req["id"], req["type"])
    return jsonify(response)

@app.route('/request/get-sign', methods=['POST'])
def get_sign():
    req = request.get_json()
    response = server.sign_msg(req["body"], req["usk"], req["type"])
    return jsonify(response)

@app.route('/request/find-signatory', methods=['POST'])
def open_sign():
    req = request.get_json()
    response = server.open_sign(req["sign"], req["type"])
    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')