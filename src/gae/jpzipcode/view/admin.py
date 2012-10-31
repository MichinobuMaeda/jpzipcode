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
from jpzipcode.view import common
from jpzipcode.model import Params, Status
from jpzipcode.utils import tz

class AdminMainPage(common.BasePage):

    def get(self):
        if 'clear' in self.request.arguments():
            Status(self.is_test()).clear()
            self.redirect(self.request.path)
        else:
            self.show('admin_main.html', {
                'stts':Status(self.is_test()).get_list(),
                'text':Params().get('view'),
        })

    def post(self):
        stts = {}
        if 'clear' in self.request.arguments():
            Status(self.is_test()).clear()
        else:
            for name in self.request.arguments():
                stts[name] = self.request.get(name, default_value='')
            stts['last_mod'] = tz.nowjststr()
            Status(self.is_test()).merge(stts)
        self.redirect(self.request.url)

app = webapp2.WSGIApplication([('/admin/', AdminMainPage)])
