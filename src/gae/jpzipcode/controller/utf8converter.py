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
from jpzipcode.controller.task import Task

class Utf8Converter(Task):
    
    def __init__(self, task, cat):
        Task.__init__(self, task, cat)

    def proc(self, zi, zip_info):
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                lines.append(unicode(line, 'ms932'))
        yield ['uc_%(cat)s.csv' % {'cat':self.get_cat(),},u''.join(lines).encode('utf8')]

    def get_ext(self):
        return 'csv'
