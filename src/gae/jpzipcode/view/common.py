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
import os
from urlparse import urlparse
import webapp2
import jinja2

class BasePage(webapp2.RequestHandler):

    def get_url(self):
        return urlparse(self.request.url)

    def get_host_port(self):
        url = self.get_url()
        host = url.hostname
        port = url.port
        if port:
            return host + ":" + str(port)
        else:
            return host

    def get_base_url(self):
        return self.get_url().scheme + "://" + self.get_host_port() + "/"

    def show(self, template_name, template_values, mime_type='text/html'):
        jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.join(
                os.path.dirname(__file__), "..", "..", "template")))
        template = jinja_environment.get_template(template_name)
        self.response.headers['Content-Type'] = mime_type
        self.response.out.write(template.render(template_values))
    
    def ret_text(self, text):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(text)
