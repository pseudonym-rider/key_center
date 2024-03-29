from flask import Flask, jsonify, request
from server import Server
from pymongo import MongoClient
from datetime import datetime
from flask_jwt_extended import (JWTManager, jwt_required, get_jwt_identity)
import json
import requests
import config

app = Flask(__name__)
server = Server()

app.config['JWT_SECRET_KEY'] = config.key

jwt = JWTManager(app)


@app.route('/issue-key', methods=['GET'])
@jwt_required
def issue_key():
    response = server.issue_key(get_jwt_identity(), str(request.args['type']))
    return jsonify(response)


@app.route('/key-identifier', methods=['GET'])
@jwt_required
def key_identifier():
    return jsonify(id=get_jwt_identity())


@app.route('/receive-qr', methods=['POST'])
def receive_qr():
    req = request.get_json()

    url = "http://127.0.0.1/key-identifier"
    user_token = req["user_token"]
    store_token = req["store_token"]

    user_id = json.loads(requests.get(url, headers={'Content-Type': 'application/json',
                                                    'Authorization': 'Bearer {}'.format(user_token)}).content.decode())
    store_id = json.loads(requests.get(url, headers={'Content-Type': 'application/json',
                                                     'Authorization': 'Bearer {}'.format(
                                                         store_token)}).content.decode())

    try:
        user_id = user_id['id']
    except:
        return jsonify(code=1, msg="user token failed"), 401

    try:
        store_id = store_id['id']
    except:
        return jsonify(code=2, msg="store token failed"), 401

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
    user_to_store_collection = db.user_to_store
    store_to_user_collection = db.store_to_user

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


def isManager(user_id):
    conn = MongoClient(config.ip)
    db = conn.main_server
    member = db.member

    manager = member.find_one({'user_id': user_id})

    if manager['type'] == '3':
        if manager['grant'] == 'True':
            return True

    return False


@app.route('/get-store', methods=['POST'])
@jwt_required
def getStore():
    try:
        if not isManager(user_id=get_jwt_identity()):
            return jsonify(code=1, msg="This user is not authorized."), 401
    except Exception as e:
        return jsonify(msg="Unregistered Manager"), 401

    req = request.get_json()

    conn = MongoClient(config.ip)
    db = conn.key_center
    user_to_store = db.user_to_store

    storesSigns = user_to_store.find({'user_id': req['user_id']})
    stores = []

    for value in storesSigns:
        stores.append({
            'store_id': server.open_sign(value['store_sign'], "2")['uid'],
            'time': value['time']
        })

    return jsonify(stores)


@app.route('/get-person', methods=['POST'])
@jwt_required
def getPerson():
    try:
        if not isManager(user_id=get_jwt_identity()):
            return jsonify(code=1, msg="This user is not authorized."), 401
    except Exception as e:
        return jsonify(msg="Unregistered Manager"), 401

    req = request.get_json()

    conn = MongoClient(config.ip)
    db = conn.key_center
    store_to_user = db.store_to_user

    people = []
    for store in req['data']:
        visitor = store_to_user.find({'store_id': store['store_id']})
        for person in visitor:
            people.append({
                'user_id': server.open_sign(person['user_sign'], "1")['uid'],
                'store_id': store['store_id'],
                'time': person['time']
            })

    return jsonify(people)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80')