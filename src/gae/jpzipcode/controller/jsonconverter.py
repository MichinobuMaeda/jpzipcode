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

class JsonConverter(Task):
    
    def __init__(self, task, cat):
        Task.__init__(self, task, cat)
    
    def proc(self, zi, zip_info):
        if zip_info.filename.startswith('tsvp'):
            yield ['%(cat)s/pref.json' % {
                    'cat':self.get_cat()
                },
                self.__proc_pref(zi, zip_info)
            ]
        elif zip_info.filename.startswith('tsvc'):
            for row in self.__proc_city(zi, zip_info):
                yield ['%(cat)s/%(pref)s/city.json' % {
                        'cat':self.get_cat(),
                        'pref':row[0]
                    },
                    row[1]
                ]
        elif zip_info.filename.startswith('tsv3'):
            for row in self.__proc_addr(zi, zip_info):
                yield ['%(cat)s/%(pref)s/%(city)s.json' % {
                        'cat':self.get_cat(),
                        'pref':row[0][:2],
                        'city':row[0][2:]
                    },
                    row[1]
                ]
    
    def __proc_pref(self, zi, zip_info):
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                lines.append('"p%(code)s":"%(name)s"' % {'code':row[0], 'name':row[1]})
        data = '{%(list)s}' % {'list':u','.join(lines)}
        return data.encode('utf-8')
    
    def __proc_city(self, zi, zip_info):
        pref = None
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                if pref == None:
                    pref = row[0][:2]
                if pref != row[0][:2]:
                    data = '{%(list)s}' % {'list':u','.join(lines)}
                    yield [pref, data.encode('utf-8')]
                    pref = row[0][:2]
                    lines = []
                lines.append('"c%(code)s":"%(name)s"' % {'code':row[0], 'name':row[1]})
            data = '{%(list)s}' % {'list':u','.join(lines)}
            yield [pref, data.encode('utf-8')]
    
    def __proc_addr(self, zi, zip_info):
        city = None
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                if city == None:
                    city = row[0]
                if city != row[0]:
                    data = '[%(list)s]' % {'list':u','.join(lines)}
                    yield [city, data.encode('utf-8')]
                    city = row[0]
                    lines = []
                item = ['"z":"%(v)s"' % {'v':row[1]}]
                if row[2]:
                    item.append('"s":"%(v)s"' % {'v':row[2]})
                if row[3]:
                    if self.get_cat() == 'ken' and (row[4] or (row[5] == u'階層不明')):
                        item.append('"b":"%(v)s"' % {'v':row[3]})
                    else:
                        item.append('"n":"%(v)s"' % {'v':row[3]})
                if row[4]:
                    if self.get_cat() == 'ken':
                        item.append('"f":"%(v)s"' % {'v':row[4]})
                    else:
                        item.append('"j":"%(v)s"' % {'v':row[4]})
                if row[5]:
                    item.append('"r":"%(v)s"' % {'v':row[5]})
                lines.append('{%(item)s}' % {'item':','.join(item)})
            data = '[%(list)s]' % {'list':u','.join(lines)}
            yield [city, data.encode('utf-8')]
        pass
    
    def __proc_zip(self, zi, zip_info):
        pass
