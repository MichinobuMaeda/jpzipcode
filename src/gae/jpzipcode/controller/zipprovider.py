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
import webapp2
from google.appengine.ext import blobstore
from jpzipcode.model import Status

class ZipProvider(webapp2.RequestHandler):
    """生成物の出力"""

    def get(self):
        filename = self.request.path.replace('/download/', '')
        task = filename[0:2]
        cat = filename[3:4]
        ts = "%(y)s-%(m)s-%(d)s" % {
            'y':filename[5:9],
            'm':filename[9:11],
            'd':filename[11:13],
        }
        stts = Status()
        if stts.get("ts_ar_%(cat)s" % {'cat':cat})[0:10] != ts:
            self.error(404)
            return
        key = stts.get("key_%(task)s_%(cat)s" % {'cat':cat, 'task':task})
        blob_info = blobstore.BlobInfo(blobstore.BlobKey(key))
        zr = blob_info.open()
        self.response.headers['Content-Type'] = 'application/zip'
        self.response.out.write(zr.read())
        zr.close()

app = webapp2.WSGIApplication([('/download/.*\.zip', ZipProvider)])
