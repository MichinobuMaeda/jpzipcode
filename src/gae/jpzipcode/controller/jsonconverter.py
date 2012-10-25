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
import zipfile
from jpzipcode.controller.task import Task

class JsonConverter(Task):
    """JSON UTF-8 LF 読み無し"""
    
    prefs = None
    cities = None
    short = False
    
    def __init__(self, task, cat):
        Task.__init__(self, task, cat)

    def proc_all(self, zi, zo, stts):
        dsz = 0
        cnt = 0
        for zip_info in zi.infolist():
            if zip_info.filename.startswith('tp') or zip_info.filename.startswith('tc'):
                for data in self.proc(zi, zip_info):
                    zo.writestr(data[0], data[1], zipfile.ZIP_DEFLATED)
                    dsz += len(data[1])
                    cnt += 1
        for zip_info in zi.infolist():
            if zip_info.filename.startswith('t3'):
                for data in self.proc(zi, zip_info):
                    zo.writestr(data[0], data[1], zipfile.ZIP_DEFLATED)
                    dsz += len(data[1])
                    cnt += 1
        stts['dsz'] = dsz
        stts['cnt'] = cnt
    
    def proc_pref(self, zi, zip_info):
        self.prefs = {}
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                lines.append('"p%(code)s":"%(name)s"' % {'code':row[0], 'name':row[1]})
                self.prefs[row[0]] = row[1]
        data = '{%(list)s}' % {'list':u','.join(lines)}
        return data.encode('utf8')
    
    def proc_city(self, zi, zip_info):
        self.cities = {}
        pref = None
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                if pref == None:
                    pref = row[0][:2]
                if pref != row[0][:2]:
                    data = '{%(list)s}' % {'list':u','.join(lines)}
                    yield [pref, data.encode('utf8')]
                    pref = row[0][:2]
                    lines = []
                lines.append('"c%(code)s":"%(name)s"' % {'code':row[0], 'name':row[1]})
                self.cities[row[0]] = row[1]
            data = '{%(list)s}' % {'list':u','.join(lines)}
            yield [pref, data.encode('utf8')]
