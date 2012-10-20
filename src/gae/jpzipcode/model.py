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

class StatusStore(db.Model):
    """ステータスの永続データ"""
    seri = db.TextProperty()

class Params():

    __param = None
    
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "param.yaml")) as y:
            self.__param = yaml.load(y.read())
    
    def get(self, cat, name=None):
        if name is None:
            return self.__param[cat]
        else:
            return self.__param[cat][name]

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
        return 'status'
    
    def get(self, name):
        if name not in self.__stts:
            return None
        return self.__stts[name]
    
    def set(self, name, val):
        self.__stts[name] = val
        self.__update()
    
    def get_list(self):
        arr = []
        for name in Params().get('param_names'):
            if name in self.__stts:
                arr.append((name, self.__stts[name]))
            else:
                arr.append([name, None])
        return arr
    
    def get_map(self):
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
        for key in stts.keys():
            self.__stts[key] = stts[key]
        self.__update()

    def clear(self, last_mod):
        for key in self.__stts.keys():
            self.__stts[key] = ''
        self.__stts['last_mod'] = last_mod
        self.__update()

    def __update(self):
        self.__init_param()
        store = StatusStore.get_by_key_name(key_names=self.get_key_name())
        store.seri = json.dumps(self.__stts, ensure_ascii=False)
        store.put()
        self.__cli.cas(self.get_key_name(), store.seri)

    def __init_param(self):
        if self.__is_test:
            initparam = Params().get('param_ini_test')
        else:
            initparam = Params().get('param_ini')
        initparam['last_mod'] = tz.nowjststr()
        for key in initparam.keys():
            if key not in self.__stts or self.__stts[key] == '':
                self.__stts[key] = initparam[key]

def save_blob(data, filename, mimetype='application/zip'):
    """Blobstore にデータを保存する。
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

class Release(Status):
    """リリース物のステータス"""

    def __init__(self, is_test=False):
        Status.__init__(self, is_test)
    
    def get_key_name(self):
        return 'release'
    
    def reflesh(self):
        stts = {}
        for item in Status().get_list():
            key = item[0]
            val = item[1]
            stts[key] = val
        self.merge(stts)
