#!/usr/bin/python
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
"""
ディレクトリ配下のJson形式のファイルの書式をチェックするツール
"""
import argparse
import json
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', nargs='?', default='./')
    args = parser.parse_args()
    if not os.path.exists(args.dir):
        print args.dir + ' is not exists.'
    for root, dirs, files in os.walk(args.dir):
        for name in files:
            print os.path.join(root, name)
            with open(os.path.join(root, name)) as f:
                json.load(f, 'utf-8')

if __name__ == '__main__':
    main()
