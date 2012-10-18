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
import ConfigParser
import os
import shutil
import sys
import urllib2
from xml.dom.minidom import parse
import zipfile

def get_http_content(url):
    try:
        f = urllib2.urlopen(url)
        data = f.read()
        f.close()
    except urllib2.URLError:
        data = None
    return data

def get_element_text(node):
    text = []
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE:
            text.append(child.data)
    return ' '.join(text).strip()

def backup_and_save(path, data):
    if os.path.isfile(path):
        bak_path = path + '.bak'
        if os.path.isfile(bak_path):
            os.remove(bak_path)
        os.rename(path, bak_path)
    f = open(path, 'w')
    f.write(data)
    f.close()

def main():
    
    # 引数に設定ファイルが指定されていなければ、同じディレクトリのファイルを使用する。
    confpath = None
    if len(sys.argv) < 2:
        confpath = sys.argv[0].replace('.py', '.conf')
    else:
        confpath = sys.argv[1]
    if not os.path.isfile(confpath):
        print 'Error: failed to open %(confpath)s.' % {'confpath':confpath}
        return
    config = ConfigParser.ConfigParser()
    config.read(confpath)
    
    # RSS の URL
    rss_url = config.get('download', 'rss')

    # ダウンロードしたファイルを置くディレクトリ
    arc_dir = config.get('download', 'arc')
    if not os.path.isabs(arc_dir):
        arc_dir = os.path.join(os.path.dirname(__file__), arc_dir)
    if not os.path.isdir(arc_dir):
        os.makedirs(arc_dir)

    # 解凍したファイルを置くディレクトリ
    trg_dir = config.get('download', 'trg')
    if not os.path.isabs(trg_dir):
        trg_dir = os.path.join(os.path.dirname(__file__), trg_dir)

    # ダウンロードするファイルのID
    ids = []
    for trg_id in config.get('download', 'ids').split(','):
        ids.append(trg_id.strip())
    
    # RSS の更新の有無を確認する。
    rss_path = os.path.join(arc_dir, 'feed.rss')
    rss = get_http_content(rss_url)
    if rss is None:
        print 'Error: failed to get %(rss_url)s.' % {'rss_url':rss_url}
        return
    if os.path.isfile(rss_path):
        f = open(rss_path)
        rss_prev = f.read()
        f.close()
        if rss_prev == rss:
            print 'Info: nothing to get.'
            return
    backup_and_save(rss_path, rss)
    
    # RSS からファイルの URL を取得し、ダウンロードする。
    zipdata = {}
    for trg_id in ids:
        zipdata[trg_id] = None
    dom = parse(rss_path)
    for item in dom.getElementsByTagName('item'):
        title = get_element_text(item.getElementsByTagName('title')[0])
        for trg_id in ids:
            if title.startswith(trg_id + ':'):
                link = get_element_text(item.getElementsByTagName('link')[0])
                zipdata[trg_id] = get_http_content(link)
                if zipdata[trg_id]:
                    continue
                print 'Error: failed to get %(rss_url)s.' % {'rss_url':rss_url}
                return
    
    # ダウンロードしたファイルを保存する。
    for trg_id in ids:
        arc_path = os.path.join(arc_dir, '%(trg_id)s.zip' % {'trg_id':trg_id})
        backup_and_save(arc_path, zipdata[trg_id])
    
    # ファイルを解凍する。
    for trg_id in ids:
        arc_path = os.path.join(arc_dir, '%(trg_id)s.zip' % {'trg_id':trg_id})
        wk_dir = trg_dir + '_wk'
        if os.path.isdir(wk_dir):
            shutil.rmtree(wk_dir)
        os.makedirs(wk_dir)
        z = zipfile.ZipFile(arc_path)
        z.extractall(wk_dir)
        z.close()
    if os.path.isdir(trg_dir):
        bak_dir = trg_dir + '_bak'
        if os.path.isdir(bak_dir):
            shutil.rmtree(bak_dir)
        os.rename(trg_dir, bak_dir)
    os.rename(wk_dir, trg_dir)

if __name__ == "__main__":
    main()
