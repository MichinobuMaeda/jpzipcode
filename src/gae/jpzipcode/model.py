# -*- coding: UTF-8 -*-
#
# Copyright 2012 Michinobu Maeda.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""データモデル"""
import json
import yaml
import os
from google.appengine.api import files
from google.appengine.api import memcache
from google.appengine.ext import blobstore
from google.appengine.ext import db
from jpzipcode.utils import tz

class Params():
    """設定"""

    __param = None
    
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "param.yaml")) as y:
            self.__param = yaml.load(y.read())
    
    def get(self, cat, name=None):
        if name is None:
            return self.__param[cat]
        else:
            return self.__param[cat][name]

class StatusStore(db.Model):
    """
    ステータスの永続データ
        ステータスのキー：値をJSON形式にシリアライズして格納する。
    """
    seri = db.TextProperty()

class Status():
    """ステータス"""

    __cli = None
    __stts = {}
    __is_test = False
    
    def __init__(self, is_test=False):
        self.__is_test = is_test
        self.__cli = memcache.Client()
        seri = self.__cli.gets(self.get_key_name())
        if seri is None:
            store = StatusStore.get_or_insert(key_name=self.get_key_name())
            seri = store.seri
            if seri is None:
                self.__init_param()
                seri = json.dumps(self.__stts, ensure_ascii=False)
                store.seri = seri
                store.put()
            self.__cli.add(self.get_key_name(), seri)
            seri = self.__cli.gets(self.get_key_name())
        self.__stts = json.loads(seri)
    
    def get_key_name(self):
        """データストアに格納するためのキー値を取得する。"""
        return 'status'
    
    def get(self, name):
        """値を取得する。"""
        if name not in self.__stts:
            return None
        return self.__stts[name]
    
    def set(self, name, val):
        """値を設定する。"""
        self.__stts[name] = val
        self.__update()
    
    def get_list(self):
        """リスト形式で全ての値を取得する。並び順は設定に従う。"""
        arr = []
        for name in Params().get('param_names'):
            if name in self.__stts:
                arr.append((name, self.__stts[name]))
            else:
                arr.append([name, None])
        return arr
    
    def get_map(self):
        """ディクショナリ形式で全ての値を取得する。"""
        param = {}
        for item in self.get_list():
            key = item[0]
            val = item[1]
            if key.startswith('csz') or key.startswith('dsz'):
                if val:
                    val = "{:,}".format(int(val))
            param[key] = val
        return param

    def merge(self, stts):
        """キー：値のセットをマージする。"""
        for key in stts.keys():
            self.__stts[key] = stts[key]
        self.__update()

    def clear(self):
        """値を初期化する。"""
        for key in self.__stts.keys():
            self.__stts[key] = ''
        self.__update()

    def __update(self):
        """
        値をデータストアに格納する。
            値が空の場合は初期値を設定する。
        """
        self.__init_param()
        store = StatusStore.get_by_key_name(key_names=self.get_key_name())
        store.seri = json.dumps(self.__stts, ensure_ascii=False)
        store.put()
        self.__cli.cas(self.get_key_name(), store.seri)

    def __init_param(self):
        """
        空の値に初期値を設定する。
            初期値は設定の param_ini または param_ini_test
        """
        if self.__is_test:
            initparam = Params().get('param_ini_test')
        else:
            initparam = Params().get('param_ini')
        initparam['last_mod'] = tz.nowjststr()
        for key in initparam.keys():
            if key not in self.__stts or self.__stts[key] == '':
                self.__stts[key] = initparam[key]

class Release(Status):
    """リリース物のステータス"""

    def __init__(self, is_test=False):
        Status.__init__(self, is_test)
    
    def get_key_name(self):
        """データストアに格納するためのキー値を取得する。"""
        return 'release'
    
    def reflesh(self):
        """ステータスを反映する。"""
        stts = {}
        for item in Status().get_list():
            key = item[0]
            val = item[1]
            stts[key] = val
        self.merge(stts)

def save_blob(data, filename, mimetype='application/zip'):
    """
    Blobstore にデータを保存する。
    Args:
        data: データ
        filename: ファイル名
        mimetype: MIME Type
    """
    blob_filename = files.blobstore.create(
        mime_type=mimetype,
        _blobinfo_uploaded_filename=filename)
    with files.open(blob_filename, 'a') as f:
        f.write(data)
    files.finalize(blob_filename)
    return str(files.blobstore.get_blob_key(blob_filename))
