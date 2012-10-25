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
from jpzipcode.model import Params, Release
from jpzipcode.view import common

class ShowMainPage(common.BasePage):

    def get(self):
        is_test = self.get_host_port().startswith('localhost:')
        self.show('show_main.html', {
            'stts':Release(is_test).get_map(),
            'text':Params().get('view'),
        })

class NoticePage(common.BasePage):

    def get(self):
        self.show('notice.html', {
            'text':Params().get('view'),
        })

app = webapp2.WSGIApplication([
    ('/', ShowMainPage),
    ('/notice.html', NoticePage),
])
