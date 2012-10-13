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

class Tsv2Converter(Task):
    
    def __init__(self, task, cat):
        Task.__init__(self, task, cat)
    
    def proc(self, zi, zip_info):
        data = None
        if self.get_cat() == 'ken':
            data = self.__proc_ken(zi, zip_info)
        elif self.get_cat() == 'jig':
            data = self.__proc_jig(zi, zip_info)
        yield ['tsv2_%(cat)s.txt' % {'cat':self.get_cat(),},data,]
    
    def __proc_ken(self, zi, zip_info):
        lines = []
        with zi.open(zip_info) as r:
            row5 = None
            row8 = None
            for line in r:
                row = unicode(line, 'utf8').split(u'\t')
                if u"（" in row[8] and u"）" not in row[8]:
                    row5 = row[5]
                    row8 = row[8]
                elif row8 is not None and u"）" in row[8]:
                    if u'(' in row5:
                        row5 += row[5]
                    row8 += row[8]
                    row[5] = row5
                    row[8] = row8
                    row5 = None
                    row8 = None
                elif row8 is not None:
                    if u'(' in row5:
                        row5 += row[5]
                    row8 += row[8]
                if row8 is None:
                    lines.append(u'\t'.join(row))
        return u''.join(lines).encode('utf-8')
    
    def __proc_jig(self, zi, zip_info):
        return zi.read(zip_info)

    def get_ext(self):
        return 'txt'
