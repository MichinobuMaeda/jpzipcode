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
    
    __tsk = None
    __cat = None
    __stt = None

    def __init__(self, task, cat):
        self.__tsk = task
        self.__cat = cat
        self.__stt = Status()

    def get_task(self):
        return self.__tsk
    
    def get_cat(self):
        return self.__cat
    
    def get_prev(self):
        return Params().get('job_prv', self.__tsk)
        
    def __get_key(self, name):
        return '%(nam)s_%(tsk)s_%(cat)s' % {
            'nam':name,
            'tsk':self.__tsk,
            'cat':self.__cat,
        }
        
    def __get_key_prev(self, name):
        return '%(nam)s_%(prv)s_%(cat)s' % {
            'nam':name,
            'prv':self.get_prev(),
            'cat':self.__cat,
        }
        
    def get_ts(self):
        return self.__stt.get('ts_arch_%(cat)s' % {'cat':self.__cat})

    def get_ts_short(self):
        return self.get_ts().replace('-', '').replace(':', '').replace(' ', '')[0:8]
    
    def get_stt(self, name):
        return self.__stt.get(self.__get_key(name))
        
    def get_stt_prev(self, name):
        return self.__stt.get(self.__get_key_prev(name))

    def set_stt(self, stt):
        dic = {}
        for key in stt.keys():
            dic[self.__get_key(key)] = stt[key]
        self.__stt.merge(dic)
    
    def kick(self):
        return self.convert()
    
    def convert(self):
        dsz = 0
        cnt = 0
        stts = {}
        key = self.get_stt_prev('key')
        blob_info = blobstore.BlobInfo(blobstore.BlobKey(key))
        zr = blob_info.open()
        zi = zipfile.ZipFile(zr, 'r')
        if len(zi.infolist()) != 1:
            zi.close()
            zr.close()
            return None
        for zip_info in zi.infolist():
            zw = StringIO.StringIO()
            zo = zipfile.ZipFile(zw, 'w', zipfile.ZIP_DEFLATED)
            for data in self.proc(zi, zip_info):
                zo.writestr(data[0], data[1], zipfile.ZIP_DEFLATED)
                dsz += len(data[1])
                cnt += 1
            zo.close()
            stts['dsz'] = dsz
            stts['cnt'] = cnt
            break
        zi.close()
        zr.close()
        con = zw.getvalue()
        stts['csz'] = len(con)
        sha1 = hashlib.sha1()
        sha1.update(con)
        stts['dig'] = sha1.hexdigest()
        stts['key'] = save_blob(con, '%(tsk)s_%(cat)s-$(ts)s.zip' % {
            'cat':self.get_cat(),
            'tsk':self.get_task(),
            'ts':self.get_ts_short(),
        })
        self.set_stt(stts)
        return 'ok'
    
    # to be overidden
    def proc(self, zi, zip_info):
        pass
    
    # to be overidden
    def get_ext(self):
        pass
