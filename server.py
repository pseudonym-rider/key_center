#!/usr/bin/env python3
from pygroupsig import constants, groupsig
from pygroupsig import signature, identity, message
from pygroupsig import grpkey, mgrkey, memkey, gml as GML
import threading, os
import config
from pymongo import MongoClient

class Server:
    _TYPE_USER = "1"
    _TYPE_STORE = "2"

    # init function
    def __init__(self):
        self._user_gpk = None
        self._user_gml = None
        self._user_msk = None
        # self._my_user_gml_id_to_idx = {}
        # self._my_user_gml_idx_to_id = {}

        self._store_gpk = None
        self._store_gml = None
        self._store_msk = None
        # self._my_store_gml_id_to_idx = {}
        # self._my_store_gml_idx_to_id = {}

        setting = self.chek()
        self.setup(setting)

    # key check
    def chek(self):
        if not os.path.isfile("./user-gpk"):
            return False
        if not os.path.isfile("./user-msk"):
            return False
        if not os.path.isfile("./store-gpk"):
            return False
        if not os.path.isfile("./store-msk"):
            return False
        return True

    # set keys
    def setup(self, setting):
        groupsig.init(constants.BBS04_CODE, 0)
        # 세팅된 값 불러오기
        if setting:
            base64_user_gpk = base64_user_msk = None
            base64_store_gpk = base64_store_msk = None
            with open("./user-gpk", "r") as f:
                base64_user_gpk = f.readline()
            with open("./user-msk", "r") as f:
                base64_user_msk = f.readline()
            with open("./store-gpk", "r") as f:
                base64_store_gpk = f.readline()
            with open("./store-msk", "r") as f:
                base64_store_msk = f.readline()

            self._user_gpk = grpkey.grpkey_import(constants.BBS04_CODE, base64_user_gpk)
            self._user_msk = mgrkey.mgrkey_import(constants.BBS04_CODE, base64_user_msk)
            self._user_gml = GML.gml_import(constants.BBS04_CODE, bytes("./user-gml".encode()))
            self._store_gpk = grpkey.grpkey_import(constants.BBS04_CODE, base64_store_gpk)
            self._store_msk = mgrkey.mgrkey_import(constants.BBS04_CODE, base64_store_msk)
            self._store_gml = GML.gml_import(constants.BBS04_CODE, bytes("./store-gml".encode()))
            return

        # 세팅된 값 없으므로 새로 생성
        bbs04_user = groupsig.setup(constants.BBS04_CODE)
        bbs04_store = groupsig.setup(constants.BBS04_CODE)

        self._user_gpk = bbs04_user["grpkey"]
        self._user_gml = bbs04_user["gml"]
        self._user_msk = bbs04_user["mgrkey"]
        self._store_gpk = bbs04_store["grpkey"]
        self._store_gml = bbs04_store["gml"]
        self._store_msk = bbs04_store["mgrkey"]

        base64_user_gpk = grpkey.grpkey_export(self._user_gpk)
        base64_user_msk = mgrkey.mgrkey_export(self._user_msk)
        GML.gml_export(self._user_gml, bytes("./user-gml".encode()))
        base64_store_gpk = grpkey.grpkey_export(self._store_gpk)
        base64_store_msk = mgrkey.mgrkey_export(self._store_msk)
        GML.gml_export(self._store_gml, bytes("./store-gml".encode()))

        with open("./user-gpk", "w") as f:
            f.write(base64_user_gpk)
        with open("./user-msk", "w") as f:
            f.write(base64_user_msk)
        with open("./store-gpk", "w") as f:
            f.write(base64_store_gpk)
        with open("./store-msk", "w") as f:
            f.write(base64_store_msk)
        return

    # add member to my gml
    def update_my_gml(self, id, usk, group_type):
        client = MongoClient(config.ip)
        db = client.key_center
        user_id_and_idx_collection = db.user_id_and_idx
        store_id_and_idx_collection = db.store_id_and_idx

        # 항상 gml 업데이트
        if group_type == Server._TYPE_USER:
            GML.gml_export(self._user_gml, bytes("./user-gml".encode()))
        if group_type == Server._TYPE_STORE:
            GML.gml_export(self._store_gml, bytes("./store-gml".encode()))

        grpkey, mgrkey, gml, my_gml_mongo = None, None, None, None

        if group_type == Server._TYPE_USER:
            grpkey = self._user_gpk
            mgrkey = self._user_msk
            gml = self._user_gml
            my_gml_mongo = user_id_and_idx_collection
        if group_type == Server._TYPE_STORE:
            grpkey = self._store_gpk
            mgrkey = self._store_msk
            gml = self._store_gml
            my_gml_mongo = store_id_and_idx_collection

        sign = groupsig.sign("valid", usk, grpkey)
        member = groupsig.open(sign, mgrkey, grpkey, gml)
        mem_id = identity.identity_to_string(member)

        doc = {
            "id": id,
            "idx": mem_id,
        }
        my_gml_mongo.insert(doc)

    # add member and issue user secret key
    def issue_key(self, id, group_type):
        usk = None
        if group_type == Server._TYPE_USER:
            msg1 = groupsig.join_mgr(0, self._user_msk, self._user_gpk,
                                     gml=self._user_gml)
            msg2 = groupsig.join_mem(1, self._user_gpk, msg1)
            usk = msg2["memkey"]
        if group_type == Server._TYPE_STORE:
            msg1 = groupsig.join_mgr(0, self._store_msk, self._store_gpk,
                                     gml=self._store_gml)
            msg2 = groupsig.join_mem(1, self._store_gpk, msg1)
            usk = msg2["memkey"]

        t = threading.Thread(target=self.update_my_gml, args=(id, usk, group_type))
        t.start()

        base64_gpk = grpkey.grpkey_export(self._user_gpk)
        base64_usk = memkey.memkey_export(usk)
        return {"gpk": base64_gpk, "usk": base64_usk}

    # sign message and return sign
    def sign_msg(self, body, base64_user_secret, base64_store_secret):
        user_grpkey = self._user_gpk
        store_grpkey = self._store_gpk
        user_secret = memkey.memkey_import(constants.BBS04_CODE, base64_user_secret)
        store_secret = memkey.memkey_import(constants.BBS04_CODE, base64_store_secret)

        user_sign = groupsig.sign(body, user_secret, user_grpkey)
        store_sign = groupsig.sign(body, store_secret, store_grpkey)

        base64_user_sign = signature.signature_export(user_sign)
        base64_store_sign = signature.signature_export(store_sign)

        return {"user_sign": base64_user_sign, "store_sign": base64_store_sign}

    # open message and return signatory's id
    def open_sign(self, base64_sign, group_type):
        client = MongoClient(config.ip)
        db = client.key_center
        user_id_and_idx_collection = db.user_id_and_idx
        store_id_and_idx_collection = db.store_id_and_idx

        mgrkey, grpkey, gml, my_gml_mongo = None, None, None, None

        if group_type == Server._TYPE_USER:
            mgrkey = self._user_msk
            grpkey = self._user_gpk
            gml = self._user_gml
            my_gml_mongo = user_id_and_idx_collection
        if group_type == Server._TYPE_STORE:
            mgrkey = self._store_msk
            grpkey = self._store_gpk
            gml = self._store_gml
            my_gml_mongo = store_id_and_idx_collection

        sign = signature.signature_import(constants.BBS04_CODE, base64_sign)
        member = groupsig.open(sign, mgrkey, grpkey, gml)
        mem_id = identity.identity_to_string(member)

        if group_type == Server._TYPE_USER:
            user_id = db.user_id_and_idx.find_one({'idx': mem_id})
        if group_type == Server._TYPE_STORE:
            user_id = db.store_id_and_idx.find_one({'idx': mem_id})

        if user_id is None:
            return {"uid": "Null"}

        return {"uid": user_id['id']}
