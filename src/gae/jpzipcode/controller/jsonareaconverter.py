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
from jpzipcode.controller.jsonconverter import JsonConverter

class JsonAreaConverter(JsonConverter):
    """JSON UTF-8 LF 読み無し 自治体別"""
    
    def __init__(self, task, cat):
        JsonConverter.__init__(self, task, cat)
    
    def proc(self, zi, zip_info):
        if zip_info.filename.startswith('tp'):
            yield ['%(cat)s/pref.json' % {
                    'cat':self.get_cat()
                },
                self.proc_pref(zi, zip_info)
            ]
        elif zip_info.filename.startswith('tc'):
            for row in self.proc_city(zi, zip_info):
                yield ['%(cat)s/%(pref)s/city.json' % {
                        'cat':self.get_cat(),
                        'pref':row[0]
                    },
                    row[1]
                ]
        elif zip_info.filename.startswith('t3'):
            for row in self.__proc_addr(zi, zip_info):
                yield ['%(cat)s/%(pref)s/%(city)s.json' % {
                        'cat':self.get_cat(),
                        'pref':row[0][:2],
                        'city':row[0][2:]
                    },
                    row[1]
                ]
    
    def __proc_addr(self, zi, zip_info):
        city = None
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                if city == None:
                    city = row[0]
                if city != row[0]:
                    data = self.__format_data(city, lines)
                    yield [city, data.encode('utf8')]
                    city = row[0]
                    lines = []
                item = ['"z":"%(v)s"' % {'v':row[1]}]
                if row[2]:
                    item.append('"s":"%(v)s"' % {'v':row[2]})
                if row[3]:
                    if self.get_cat() == 'k' and (row[4] or (row[5] == u'階層不明')):
                        item.append('"b":"%(v)s"' % {'v':row[3]})
                    else:
                        item.append('"n":"%(v)s"' % {'v':row[3]})
                if row[4]:
                    if self.get_cat() == 'k':
                        item.append('"f":"%(v)s"' % {'v':row[4]})
                    else:
                        item.append('"j":"%(v)s"' % {'v':row[4]})
                if row[5]:
                    item.append('"r":"%(v)s"' % {'v':row[5]})
                lines.append('{%(item)s}' % {'item':','.join(item)})
            data = self.__format_data(city, lines)
            yield [city, data.encode('utf8')]
    
    def __format_data(self, city, lines):
        if self.short:
            return '[\n%(list)s\n]' % {
                'list':u',\n'.join(lines),
            }
        else:
            return '{"p":{"c":"%(pc)s","n":"%(pn)s"},"c":{"c":"%(cc)s","n":"%(cn)s"},"a":[\n%(list)s\n]}' % {
                'pc':city[:2],
                'pn':self.prefs[city[:2]],
                'cc':city,
                'cn':self.cities[city],
                'list':u',\n'.join(lines),
            }

class JsonAreaShortConverter(JsonAreaConverter):
    """JSON UTF-8 LF 読み無し 自治体別 短め"""

    def __init__(self, task, cat):
        JsonAreaConverter.__init__(self, task, cat)
        self.short = True
