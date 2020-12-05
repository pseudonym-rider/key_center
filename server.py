#!/usr/bin/env python3
from pygroupsig import grpkey, constants, groupsig
from pygroupsig import signature, identity, message
from pygroupsig import grpkey, mgrkey, memkey, gml
import threading


class Server:
    _TYPE_USER = "1"
    _TYPE_STORE = "2"
    
    # init function
    def __init__(self):
        self._user_gpk = None
        self._user_gml = None
        self._user_msk = None
        self._my_user_gml_id_to_idx = {}
        self._my_user_gml_idx_to_id = {}
        
        self._store_gpk = None
        self._store_gml = None
        self._store_msk = None
        self._my_store_gml_id_to_idx = {}
        self._my_store_gml_idx_to_id = {}
        
        self.setup()
    
    # set keys
    def setup(self):
        groupsig.init(constants.BBS04_CODE, 0)
        bbs04_user = groupsig.setup(constants.BBS04_CODE)
        bbs04_store = groupsig.setup(constants.BBS04_CODE)
        
        self._user_gpk = bbs04_user["grpkey"]
        self._user_gml = bbs04_user["gml"]
        self._user_msk = bbs04_user["mgrkey"]
        self._store_gpk = bbs04_store["grpkey"]
        self._store_gml = bbs04_store["gml"]
        self._store_msk = bbs04_store["mgrkey"]
    
    # add member to my gml
    def update_my_gml(self, id, usk, group_type):
        grpkey, mgrkey, gml, my_id_to_idx, my_idx_to_id \
            = None, None, None, None, None
        
        if group_type == Server._TYPE_USER:
            grpkey = self._user_gpk
            mgrkey = self._user_msk
            gml = self._user_gml
            my_id_to_idx = self._my_user_gml_id_to_idx
            my_idx_to_id = self._my_user_gml_idx_to_id
        if group_type == Server._TYPE_STORE:
            grpkey = self._store_gpk
            mgrkey = self._store_msk
            gml = self._store_gml
            my_id_to_idx = self._my_store_gml_id_to_idx
            my_idx_to_id = self._my_store_gml_idx_to_id
        
        sign = groupsig.sign("valid", usk, grpkey)
        member = groupsig.open(sign, mgrkey, grpkey, gml)
        mem_id = identity.identity_to_string(member)
        
        my_idx_to_id[mem_id] = id
        if my_id_to_idx.get(id) == None:
            my_id_to_idx[id] = list(mem_id)
        else:
            my_id_to_idx[id].append(mem_id)
    
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
        return {"gpk":base64_gpk, "usk":base64_usk}
    
    # sign message and return sign
    def sign_msg(self, body, base64_usk, group_type):
        grpkey = self._user_gpk if group_type == Server._TYPE_USER else self._store_gpk
        usk = memkey.memkey_import(constants.BBS04_CODE, base64_usk)
        
        sign = groupsig.sign(body, usk, grpkey)
        base64_sign = signature.signature_export(sign)
        return {"sign":base64_sign}
    
    # open message and return signatory's id
    def open_sign(self, base64_sign, group_type):
        mgrkey, grpkey, gml, my_idx_to_id = None, None, None, None
        
        if group_type == Server._TYPE_USER:
            mgrkey = self._user_msk
            grpkey = self._user_gpk
            gml = self._user_gml
            my_idx_to_id = self._my_user_gml_idx_to_id
        if group_type == Server._TYPE_STORE:
            mgrkey = self._store_msk
            grpkey = self._store_gpk
            gml = self._store_gml
            my_idx_to_id = self._my_store_gml_idx_to_id
        
        sign = signature.signature_import(constants.BBS04_CODE, base64_sign)
        member = groupsig.open(sign, mgrkey, grpkey, gml)
        mem_id = identity.identity_to_string(member)
        user_id = my_idx_to_id[mem_id]
        
        return {"uid":user_id}