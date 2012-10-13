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
"""ジョブ・コントローラ"""
import webapp2
from google.appengine.api import taskqueue
from jpzipcode.view import common
from jpzipcode.controller.sourcechecker import SourceChecker
from jpzipcode.controller.utf8converter import Utf8Converter
from jpzipcode.controller.tsv1converter import Tsv1Converter
from jpzipcode.controller.tsv2converter import Tsv2Converter
from jpzipcode.controller.tsv3converter import Tsv3Converter
from jpzipcode.controller.jsonconverter import JsonConverter
from jpzipcode.model import Params, Status, Release
from jpzipcode.utils import tz

class JobKicker(common.BasePage):
    
    # Jobクラス
    __jobs = {
        'page':SourceChecker,
        'arch':SourceChecker,
        'utf8':Utf8Converter,
        'tsv1':Tsv1Converter,
        'tsv2':Tsv2Converter,
        'tsv3':Tsv3Converter,
        'json':JsonConverter,
    }
    
    # HTTP GET
    def get(self):
        self.post()
    
    # HTTP POST
    def post(self):
        params = self.request.path.split('/')
        ctrl = None
        ret = 'ok'
        if len(params) < 4:
            ret = 'Error: Path: %(path)s' % {'path':self.request.path}
        else:
            name = params[2]
            cat  = params[3]
            if name not in self.__jobs:
                ret = 'Error: Path: %(path)s' % {'path':self.request.path}
        if ret != 'ok':
            self.ret_text(ret)
            return
        if len(params) > 4:
            ctrl = params[4]
        job = self.__jobs[name](name, cat)
        if ctrl == 'reg' and len(params) > 5:
            taskqueue.add(url='/job/%(name)s/%(cat)s' % {'name':name, 'cat':cat})
            self.redirect('/' + '/'.join(params[5:]))
            return
        elif not job.kick():
            ret = 'Error: Failed: %(path)s' % {'path':self.request.path}
        elif ctrl == 'stop':
            ret = 'stop'
        else:
            succ = Params().get('job_succ', name)
            if succ is None:
                Status().set('updated_%(cat)s' % {'cat':cat}, tz.nowjststr())
                Status().set('updated', tz.nowjststr())
                Release().reflesh()
                ret = 'stop'
        self.ret_text(ret)
        if ret == 'ok':
            taskqueue.add(url='/job/%(name)s/%(cat)s' % {'name':succ, 'cat':cat})

app = webapp2.WSGIApplication([('/job/.*', JobKicker)])
