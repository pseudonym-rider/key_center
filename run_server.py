from flask import Flask, jsonify, request
from server import Server
from pymongo import MongoClient
from datetime import datetime
import config

app = Flask(__name__)
server = Server()
client = MongoClient(config.ip)
qr_db = client.qr_db
user_to_store_collection = qr_db.user_to_store
store_to_user_collection = qr_db.store_to_user


@app.route('/request/issue-key', methods=['POST'])
def issue_key():
    req = request.get_json()
    response = server.issue_key(req["id"], req["type"])
    return jsonify(response)


@app.route('/request/find-signatory', methods=['POST'])
def open_sign():
    req = request.get_json()
    response = server.open_sign(req["sign"], req["type"])
    return jsonify(response)


@app.route('/receive-qr', methods=['POST'])
def receive_qr():
    req = request.get_json()

    user_id = req["user_id"]
    store_id = req["store_id"]
    qr_time = req["time"]
    user_secret = req["user_secret"]
    store_secret = req["store_secret"]

    now_time = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()

    # check validation of time
    if now_time - int(qr_time) >= 15:
        return jsonify({"response": False})

    user_data = user_id + "?" + qr_time
    store_data = store_id + "?" + qr_time

    # user-data and store-data contain each id and qr-time
    signs_of_user_data = server.sign_msg(user_data, user_secret, store_secret)
    signs_of_store_data = server.sign_msg(store_data, user_secret, store_secret)

    # save qr code to db
    doc = {
        "user_id": user_id,
        "time": qr_time,
        "user_sign": signs_of_user_data["user_sign"],
        "store_sign": signs_of_user_data["store_sign"]
    }
    user_to_store_collection.insert(doc)
    doc = {
        "store_id": store_id,
        "time": qr_time,
        "user_sign": signs_of_store_data["user_sign"],
        "store_sign": signs_of_store_data["store_sign"]
    }
    store_to_user_collection.insert(doc)

    return jsonify({"response": True})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')