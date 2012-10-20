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

class Tsv3Converter(Task):
    
    def __init__(self, task, cat):
        Task.__init__(self, task, cat)
    
    def proc(self, zi, zip_info):
        if self.get_cat() == 'k':
            yield ['tp_%(cat)s.txt' % {'cat':self.get_cat()},self.__proc_k_pref(zi, zip_info)]
            yield ['tc_%(cat)s.txt' % {'cat':self.get_cat()},self.__proc_k_city(zi, zip_info)]
            yield ['t3_%(cat)s.txt' % {'cat':self.get_cat()},self.__proc_k_addr(zi, zip_info)]
        elif self.get_cat() == 'j':
            yield ['tp_%(cat)s.txt' % {'cat':self.get_cat()},self.__proc_j_pref(zi, zip_info)]
            yield ['tc_%(cat)s.txt' % {'cat':self.get_cat()},self.__proc_j_city(zi, zip_info)]
            yield ['t3_%(cat)s.txt' % {'cat':self.get_cat()},self.__proc_j_addr(zi, zip_info)]
    
    def __proc_k_pref(self, zi, zip_info):
        code = None
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                if code != row[0][:2]:
                    code = row[0][:2]
                    lines.append(u'\t'.join([code, row[6], row[3]]))
        lines.append('')
        return u'\n'.join(lines).encode('utf8')
    
    def __proc_j_pref(self, zi, zip_info):
        code = None
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                if code != row[0][:2]:
                    code = row[0][:2]
                    lines.append(u'\t'.join([code, row[3], '']))
        lines.append('')
        return u'\n'.join(lines).encode('utf8')
    
    def __proc_k_city(self, zi, zip_info):
        code = None
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                if code != row[0]:
                    code = row[0]
                    lines.append(u'\t'.join([code, row[7], row[4]]))
        lines.append('')
        return u'\n'.join(lines).encode('utf8')
    
    def __proc_j_city(self, zi, zip_info):
        code = None
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                if code != row[0]:
                    code = row[0]
                    lines.append(u'\t'.join([code, row[4], '']))
        lines.append('')
        return u'\n'.join(lines).encode('utf8')
    
    def __proc_k_addr(self, zi, zip_info):
        lines = []
        with zi.open(zip_info) as r:
            add1len = None
            yom1len = None
            add1bldg = None
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                add1 = row[8]
                add2 = ''
                add3 = ''
                note = ''
                yom1 = row[5]
                yom2 = ''
                yom3 = ''
                if u"（" in add1 and u"）" in add1:
                    beg = add1.rindex(u"（")
                    end = add1.rindex(u"）")
                    if u"）" in add1[beg+1:end]:
                        beg = add1.rindex(u"（", 0, beg)
                    add2 = add1[beg+1:end]
                    add1 = add1[:beg]
                if u"(" in yom1 and u")" in yom1:
                    beg = yom1.rindex(u"(")
                    end = yom1.rindex(u")")
                    if u")" in yom1[beg+1:end]:
                        beg = yom1.rindex(u"(", 0, beg)
                    yom2 = yom1[beg+1:end]
                    yom1 = yom1[:beg]
                if u"以下に掲載がない場合" == add1 \
                or u"村一円" in add1 or u"町一円" in add1 or u"無番地" in add1:
                    note = add1
                    add1 = ''
                    yom1 = ''
                elif u"丁目" == add2 or u"番地" == add2 or u"無番地" in add2 \
                or u"その他" in add2 or u"以上" in add2 \
                or u"を除く" in add2 or u"○" in add2:
                    note = add2
                    add2 = ''
                    yom2 = ''
                    if note == u'次のビルを除く':
                        add1len = len(add1)
                        yom1len = len(yom1)
                elif add2 == u'地階・階層不明':
                    add1bldg = add1
                    add2 = add1[add1len:]
                    add3 = u'地階'
                    yom2 = yom1[yom1len:]
                    yom3 = u'ﾁｶｲ'
                    add1 = add1[:add1len]
                    yom1 = yom1[:yom1len]
                    lines.append(u'\t'.join([
                        row[0],
                        row[2],
                        add1,
                        add1bldg[add1len:],
                        '',
                        u'階層不明',
                        yom1,
                        yom2,
                        '',
                        row[9],
                        row[10],
                        row[11],
                        row[12],
                        row[13],
                        row[14],
                        '',
                        '',
                    ]))
                elif add1len is not None:
                    if add1 == add1bldg:
                        add3 = add2
                        add2 = add1[add1len:]
                        yom3 = yom2
                        yom2 = yom1[yom1len:]
                        add1 = add1[:add1len]
                        yom1 = yom1[:yom1len]
                    else:
                        add1len = None
                        yom1len = None
                        add1bldg = None
                lines.append(u'\t'.join([
                    row[0],
                    row[2],
                    add1,
                    add2,
                    add3,
                    note,
                    yom1,
                    yom2,
                    yom3,
                    row[9],
                    row[10],
                    row[11],
                    row[12],
                    row[13],
                    row[14],
                    '',
                    '',
                ]))
        lines.append('')
        return u'\n'.join(lines).encode('utf8')
    
    def __proc_j_addr(self, zi, zip_info):
        lines = []
        with zi.open(zip_info) as r:
            for line in r:
                row = unicode(line.rstrip(), 'utf8').split(u'\t')
                lines.append(u'\t'.join([
                    row[0],
                    row[7],
                    row[5],
                    row[6],
                    row[2],
                    '',
                    '',
                    '',
                    row[1],
                    row[11],
                    '',
                    '',
                    '',
                    row[12],
                    '',
                    row[10],
                    row[9],
                ]))
        lines.append('')
        return u'\n'.join(lines).encode('utf8')

    def get_ext(self):
        return 'txt'
