from flask import Flask, jsonify, request
from server import Server
from pymongo import MongoClient
from datetime import datetime
import config

app = Flask(__name__)
server = Server()


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

    conn = MongoClient(config.ip)
    db = conn.key_center
    user_to_store = db.user_to_store
    store_to_user = db.store_to_user

    # save qr code to db
    doc = {
        "user_id": user_id,
        "time": qr_time,
        "user_sign": signs_of_user_data["user_sign"],
        "store_sign": signs_of_user_data["store_sign"]
    }
    user_to_store.insert(doc)
    doc = {
        "store_id": store_id,
        "time": qr_time,
        "user_sign": signs_of_store_data["user_sign"],
        "store_sign": signs_of_store_data["store_sign"]
    }
    store_to_user.insert(doc)

    return jsonify({"response": True})


@app.route('/get-store', methods=['GET'])
def getStore():
    req = request.get_json()

    conn = MongoClient(config.ip)
    db = conn.key_center
    user_to_store = db.user_to_store
    store_to_user = db.store_to_user

    storesSigns = user_to_store.find({'user_id': req['user_id']})
    stores = []

    for value in storesSigns:
        stores.append({
            'store_id': server.open_sign(value['store_sign'], '2'),
            'time': value['time']
        })

    return jsonify(stores)


@app.route('/get-person', methods=['POST'])
def getPerson():
    req = request.get_json()

    conn = MongoClient(config.ip)
    db = conn.key_center
    store_to_user = db.store_to_user

    people = []
    for store in req['data']:
        store


@app.route('/get-data', methods=['POST'])
def getData():
    req = request.get_json()

    conn = MongoClient(config.ip)
    db = conn.key_center
    user_to_store = db.user_to_store
    store_to_user = db.store_to_user

    storesSigns = user_to_store.find({'user_id': req['user_id']})
    stores = []

    for value in storesSigns:
        stores.append(server.open_sign(value, '2'))

    return jsonify(stores)
    '''
    user_to_store_collection의 
    개인 id 입력 -> 방문한 점포 sign을 모두 찾음(sSigns)
    -> 찾은 점포 sign을 오픈하여 점포 id를 찾음
    -> 찾은 점포 id에 방문한 모든 사용자의 sign 을 찾음
    -> 찾은 sign을 open하여 user_id를 찾음
    -> 찾은 user_id를 통해 user의 정보를 모두 반환함
    '''


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')