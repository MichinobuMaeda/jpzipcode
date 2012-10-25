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
import hashlib
import StringIO
import zipfile
from google.appengine.ext import blobstore
from jpzipcode.model import Params, Status, save_blob

class Task():
    """タスク"""
    
    __tsk = None
    __cat = None
    __stt = None

    def __init__(self, task, cat):
        self.__tsk = task
        self.__cat = cat
        self.__stt = Status()

    def get_task(self):
        """タスク名を取得する。"""
        return self.__tsk
    
    def get_cat(self):
        """分類(住所/事業所)を取得する。"""
        return self.__cat
    
    def get_prev(self):
        """データのインプットになるタスク名を取得する。"""
        return Params().get('job_prv', self.__tsk)
        
    def __get_key(self, name):
        """ステータスのキーを取得する。"""
        return '%(nam)s_%(tsk)s_%(cat)s' % {
            'nam':name,
            'tsk':self.__tsk,
            'cat':self.__cat,
        }
        
    def __get_key_prev(self, name):
        """インプットデータのステータスのキーを取得する。"""
        return '%(nam)s_%(prv)s_%(cat)s' % {
            'nam':name,
            'prv':self.get_prev(),
            'cat':self.__cat,
        }
        
    def get_ts(self):
        """日本郵便配布データのタイムスタンプを取得する。"""
        return self.__stt.get('ts_ar_%(cat)s' % {'cat':self.__cat})

    def get_ts_short(self):
        """日本郵便配布データのタイムスタンプを短い書式で取得する。"""
        return self.get_ts().replace('-', '').replace(':', '').replace(' ', '')[0:8]
    
    def get_stt(self, name):
        """ステータスを取得する。"""
        return self.__stt.get(self.__get_key(name))
        
    def get_stt_prev(self, name):
        """インプットデータのステータスを取得する。"""
        return self.__stt.get(self.__get_key_prev(name))

    def set_stt(self, stt):
        """ステータスを設定する。"""
        dic = {}
        for key in stt.keys():
            dic[self.__get_key(key)] = stt[key]
        self.__stt.merge(dic)
    
    def kick(self):
        """処理を実行する。"""
        return self.convert()
    
    def convert(self):
        """データ変換処理を実行する。"""
        stts = {}
        key = self.get_stt_prev('key')
        blob_info = blobstore.BlobInfo(blobstore.BlobKey(key))
        zr = blob_info.open()
        zi = zipfile.ZipFile(zr, 'r')
        if len(zi.infolist()) < 1:
            zi.close()
            zr.close()
            return None
        zw = StringIO.StringIO()
        zo = zipfile.ZipFile(zw, 'w', zipfile.ZIP_DEFLATED)
        self.proc_all(zi, zo, stts)
        zo.close()
        zi.close()
        zr.close()
        con = zw.getvalue()
        stts['csz'] = len(con)
        sha1 = hashlib.sha1()
        sha1.update(con)
        stts['dig'] = sha1.hexdigest()
        stts['key'] = save_blob(con, '%(tsk)s_%(cat)s-%(ts)s.zip' % {
            'cat':self.get_cat(),
            'tsk':self.get_task(),
            'ts':self.get_ts_short(),
        })
        self.set_stt(stts)
        return 'ok'

    # can be overidden
    def proc_all(self, zi, zo, stts):
        """全てのインプットを処理する。"""
        dsz = 0
        cnt = 0
        for zip_info in zi.infolist():
            for data in self.proc(zi, zip_info):
                zo.writestr(data[0], data[1], zipfile.ZIP_DEFLATED)
                dsz += len(data[1])
                cnt += 1
            stts['dsz'] = dsz
            stts['cnt'] = cnt
    
    # to be overidden
    def proc(self, zi, zip_info):
        """1個のインプットを処理する。"""
        pass
