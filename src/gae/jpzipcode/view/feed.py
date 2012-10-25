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
from jpzipcode.utils import tz

class FeedRss(common.BasePage):

    def get(self):
        stts = Release()
        self.show('feed.xml', {
            'stts':stts.get_map(),
            'text':Params().get('view'),
            'base_url':self.get_base_url(),
            'pub_date':{
                'a':tz.jststr2rfc822(stts.get('upd')),
                'k':tz.jststr2rfc822(stts.get('upd_k')),
                'j':tz.jststr2rfc822(stts.get('upd_j')),
            }
        }, 'application/rss+xml')

app = webapp2.WSGIApplication([('/feed.rss', FeedRss)])
