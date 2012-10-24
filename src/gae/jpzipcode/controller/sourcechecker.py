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
import logging
import zipfile
from google.appengine.api import urlfetch
from google.appengine.ext import blobstore
from jpzipcode.controller.task import Task
from jpzipcode.utils import tz
from jpzipcode import model

class SourceChecker(Task):
    
    __headers = {'Cache-Control':'max-age=300'}
    
    def __init__(self, task, cat):
        Task.__init__(self, task, cat)
    
    def kick(self):
        url = self.get_stt('url')
        prv = self.get_stt('dig')
        res = urlfetch.fetch(url, deadline=60, headers=self.__headers)
        stts = {}
        stts['chk'] = tz.nowjststr()
        if res.status_code != 200:
            logging.error('HTTP Response: %(cd)s' % {'cd':res.status_code})
            return None
        if not res.content:
            logging.error('No content.')
            return None
        if 1 > len(res.content):
            logging.error('Content length: %(len)s' % {'len':len(res.content)})
            return None
        sha1 = hashlib.sha1()
        sha1.update(res.content)
        cur = sha1.hexdigest()
        if cur == prv:
            self.set_stt(stts)
            logging.info('Nothing to get.')
            return 'stop'
        stts['dig'] = cur
        stts['mod'] = tz.nowjststr()
        if self.get_task() == "ar":
            self.__save(res.content, self.get_cat(), stts)
        self.set_stt(stts)
        return 'ok'
    
    def __save(self, con, cat, stts):
        stts['csz'] = len(con)
        stts['key'] = model.save_blob(con, "%(cat)s.zip" % {'cat':cat})
        blob_info = blobstore.BlobInfo(blobstore.BlobKey(stts['key']))
        zr = blob_info.open()
        zi = zipfile.ZipFile(zr, 'r')
        if len(zi.infolist()) != 1:
            zi.close()
            zr.close()
            logging.error('No ZIP entry.')
            return None
        for zip_info in zi.infolist():
            t = zip_info.date_time
            stts['ts'] = "%(y)04d-%(m)02d-%(d)02d %(H)02d:%(M)02d:%(S)02d" % {
                'y':t[0], 'm':t[1], 'd':t[2], 'H':t[3], 'M':t[4], 'S':t[5]
            }
            stts['dsz'] = zip_info.file_size
            stts['cnt'] = 1
            break
        zi.close()
        zr.close()
