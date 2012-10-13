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
import datetime

class UtcTzinfo(datetime.tzinfo):
    """タイムゾーン: UTC"""
    def utcoffset(self, unused_dt):
        return datetime.timedelta(0)
    def dst(self, unused_dt):
        return datetime.timedelta(0)
    def tzname(self, unused_dt):
        return 'UTC'
    def olsen_name(self):
        return 'UTC'

class EstTzinfo(datetime.tzinfo):
    """タイムゾーン: EST"""
    def utcoffset(self, unused_dt):
        return datetime.timedelta(hours=-5)
    def dst(self, unused_dt):
        return datetime.timedelta(0)
    def tzname(self, unused_dt):
        return 'EST+05EDT'
    def olsen_name(self):
        return 'US/Eastern'

class PstTzinfo(datetime.tzinfo):
    """タイムゾーン: PST"""
    def utcoffset(self, unused_dt):
        return datetime.timedelta(hours=-8)
    def dst(self, unused_dt):
        return datetime.timedelta(0)
    def tzname(self, unused_dt):
        return 'PST+08PDT'
    def olsen_name(self):
        return 'US/Pacific'

class JstTzinfo(datetime.tzinfo):
    """タイムゾーン: Asia/Tokyo"""
    def utcoffset(self, unused_dt):
        return datetime.timedelta(hours=9)
    def dst(self, unused_dt):
        return datetime.timedelta(0)
    def tzname(self, unused_dt):
        return 'JST'
    def olsen_name(self):
        return 'Asia/Tokyo'

def nativeasjst(native):
    """タイムゾーン無しの日時に JST を設定したものを返す。"""
    if native is None:
        return None
    return native.replace(tzinfo=JstTzinfo())

def native2jst(native):
    """タイムゾーン無しの日時を UTC と見なして JST に変換したものを返す。"""
    if native is None:
        return None
    return native.replace(tzinfo=UtcTzinfo()).astimezone(JstTzinfo())

def native2jststr(native):
    """タイムゾーン無しの日時を UTC と見なして JST に変換した文字列を返す。"""
    if native is None:
        return None
    return native2jst(native).isoformat(' ')[0:19]

def nowjststr():
    """現在の日時を JST に変換した文字列を返す。"""
    return datetime.datetime.now(JstTzinfo()).isoformat(' ')[0:19]

def jststr2rfc822(str):
    """JST の文字列を RFC822 形式に変換する。"""
    if str is None or str == '':
        return ''
    dt = datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
    return dt.strftime('%a, %d %b %Y %H:%M:%S') + ' JST'
