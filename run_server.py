from flask import Flask, jsonify, request
from server import Server
from pymongo import MongoClient
from datetime import datetime
import config

app = Flask(__name__)
server = Server()
client = MongoClient("172.17.0.3")
qr_db = client.qr_db
user_to_store_collection = qr_db.user_to_store
store_to_user_collection = qr_db.store_to_user


@app.route('/request/issue-key', methods=['POST'])
def issue_key():
    req = request.get_json()
    response = server.issue_key(req["id"], req["type"])
    return jsonify(response)


# @app.route('/request/get-sign', methods=['POST'])
# def get_sign():
#     req = request.get_json()
#     response = server.sign_msg(req["body"], req["usk"], req["type"])
#     return jsonify(response)

@app.route('/request/find-signatory', methods=['POST'])
def open_sign():
    req = request.get_json()
    response = server.open_sign(req["sign"], req["type"])
    return jsonify(response)


@app.route('/receive-qr', methods=['POST'])
def receive_qr():
    req = request.get_json()

    user_id = req["user-id"]
    store_id = req["store-id"]
    qr_time = req["time"]
    user_secret = req["user-secret"]
    store_secret = req["store-secret"]

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
        "user-id": user_id,
        "time": qr_time,
        "user-sign": signs_of_user_data["user-sign"],
        "store-sign": signs_of_user_data["store-sign"]
    }
    user_to_store_collection.insert(doc)
    doc = {
        "store-id": store_id,
        "time": qr_time,
        "user-sign": signs_of_store_data["user-sign"],
        "store-sign": signs_of_store_data["store-sign"]
    }
    store_to_user_collection.insert(doc)

    return jsonify({"response": True})


# check for the succesful update
@app.route('/check-mongo', methods=['POST'])
def check_mongo():
    req = request.get_json()

    user_id = req["user-id"]
    store_id = req["store-id"]

    u2s_dict = user_to_store_collection.find({"user-id": user_id})
    s2u_dict = store_to_user_collection.find({"store-id": store_id})

    print("u2s_dict =>")
    for x in u2s_dict:
        print(x)
    print("s2u_dict =>")
    for x in s2u_dict:
        print(x)
    return jsonify({"u2s_dict": u2s_dict, "s2u_dict": s2u_dict})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')