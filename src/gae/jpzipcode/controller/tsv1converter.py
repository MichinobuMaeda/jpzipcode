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
import csv
from jpzipcode.controller.task import Task

class Tsv1Converter(Task):
    
    def __init__(self, task, cat):
        Task.__init__(self, task, cat)
    
    def proc(self, zi, zip_info):
        lines = []
        with zi.open(zip_info) as zr:
            cr = csv.reader(zr, delimiter=',', quotechar='"')
            for line in cr:
                lines.append('\t'.join(unicode(row, 'utf8') for row in line))
            lines.append('')
        yield ['tsv1_%(cat)s.txt' % {'cat':self.get_cat(),},u'\n'.join(lines).encode('utf8')]

    def get_ext(self):
        return 'txt'
