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
import logging
import webapp2
from google.appengine.api import taskqueue
from jpzipcode.view import common
from jpzipcode.controller.sourcechecker import SourceChecker
from jpzipcode.controller.utf8converter import Utf8Converter
from jpzipcode.controller.tsv1converter import Tsv1Converter
from jpzipcode.controller.tsv2converter import Tsv2Converter
from jpzipcode.controller.tsv3converter import Tsv3Converter
from jpzipcode.controller.jsonareaconverter import JsonAreaConverter, JsonAreaShortConverter
from jpzipcode.controller.jsonzipconverter import JsonZipConverter, JsonZipShortConverter
from jpzipcode.model import Params, Status, Release
from jpzipcode.utils import tz

class JobKicker(common.BasePage):
    """ジョブ実行"""
    
    # Jobクラス
    __jobs = {
        'pg':SourceChecker,
        'ar':SourceChecker,
        'uc':Utf8Converter,
        't1':Tsv1Converter,
        't2':Tsv2Converter,
        't3':Tsv3Converter,
        'ja':JsonAreaConverter,
        'jz':JsonZipConverter,
        'jb':JsonAreaShortConverter,
        'jy':JsonZipShortConverter,
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
            task = params[2]
            cat  = params[3]
            if task == 'first':
                task = Params().get('first_task', cat)
            if task not in self.__jobs:
                ret = 'Error: Path: %(path)s' % {'path':self.request.path}
        if ret != 'ok':
            self.ret_text(ret)
            return
        if len(params) > 4:
            ctrl = params[4]
        job = self.__jobs[task](task, cat)
        if ctrl == 'reg' and len(params) > 5:
            taskqueue.add(url='/job/%(task)s/%(cat)s' % {'task':task, 'cat':cat})
            self.redirect('/' + '/'.join(params[5:]))
            return
        stt = job.kick()
        if not stt:
            ret = 'Error: Failed to proc: %(path)s' % {'path':self.request.path}
        elif stt == 'stop':
            ret = 'stop'
        elif ctrl == 'stop':
            ret = 'stop'
        else:
            succ = Params().get('task_seq', task)
            if succ is None:
                Status().set('upd_%(cat)s' % {'cat':cat}, tz.nowjststr())
                Status().set('upd', tz.nowjststr())
                ret = 'end'
        self.ret_text(ret)
        if self.is_test():
            interval = Params().get('task_interval', 'test')
        else:
            interval = Params().get('task_interval', 'active')
        if ret == 'ok':
            taskqueue.add(url='/job/%(task)s/%(cat)s' % {'task':succ, 'cat':cat}, countdown=interval)
        elif ret == 'end':
            succ = Params().get('job_seq', cat)
            if succ is None:
                logging.info('Refles release status.')
                Release().reflesh()
            else:
                taskqueue.add(url='/job/first/%(cat)s' % {'cat':succ}, countdown=interval)
    
    def ret_text(self, ret):
        common.BasePage.ret_text(self, ret)
        logging.info(ret)

app = webapp2.WSGIApplication([('/job/.*', JobKicker)])
