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

class JsonZipConverter(JsonConverter):
    """JSON UTF-8 LF 読み無し 郵便番号別"""
    
    def __init__(self, task, cat):
        JsonConverter.__init__(self, task, cat)
    
    def proc(self, zi, zip_info):
        if zip_info.filename.startswith('tp'):
            yield ['pref.json' % {
                    'cat':self.get_cat()
                },
                self.proc_pref(zi, zip_info)
            ]
        elif zip_info.filename.startswith('tc'):
            for row in self.proc_city(zi, zip_info):
                yield ['%(pref)s/city.json' % {
                        'pref':row[0],
                    },
                    row[1]
                ]
        elif zip_info.filename.startswith('t3'):
            for row in self.__proc_zip(zi, zip_info):
                yield ['%(z1)s/%(z2)s.json' % {
                        'cat':self.get_cat(),
                        'z1':row[0][:3],
                        'z2':row[0][3:],
                    },
                    row[1]
                ]
    
    def __proc_zip(self, zi, zip_info):
        items = {}
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                city = row[0]
                pref = city[:2]
                z = row[1]
                item = ['"z":"%(z)s"' % {'z':z}]
                if not self.short:
                    item.append('"pc":"%(pc)s","pn":"%(pn)s"' % {'pc':pref, 'pn':self.prefs[pref]})
                    item.append('"cc":"%(cc)s","cn":"%(cn)s"' % {'cc':city, 'cn':self.cities[city]})
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
                key = z[0:5]
                if key not in items:
                    items[key] = []
                items[key].append('{%(item)s}' % {'item':','.join(item)})
        for key in items.keys():
            data = '[\n%(list)s\n]' % {'list':u',\n'.join(items[key])}
            yield [key, data.encode('utf8')]

class JsonZipShortConverter(JsonZipConverter):
    """JSON UTF-8 LF 読み無し 郵便番号別 短め"""
    
    def __init__(self, task, cat):
        JsonZipConverter.__init__(self, task, cat)
        self.short = True
