#!/bin/sh
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
UNZIP_PATH=/usr/bin/unzip
PYTHON_PATH=/usr/bin/python
CURL_PATH=/opt/local/bin/curl
#
WK_DIR="`pwd`/$( dirname "$0" )/../test/site/wk"
LOG_DIR="`pwd`/$( dirname "$0" )/../test/log"
LOG_NAME="${LOG_DIR}/test_data.log"
PY_DL_SCRIPT=`pwd`/$( dirname "$0" )/../src/download/jpzipcode_download.py
PY_DL_CONF=`pwd`/$( dirname "$0" )/../test/jpzipcode_download
JSON_CHECKER="`pwd`/$( dirname "$0" )/json_files_checker.py"

if [ ! -d ${WK_DIR} ] ; then mkdir -p ${WK_DIR} ; fi
if [ -f ${WK_DIR}/arc/feed.rss ] ; then mv -f ${WK_DIR}/arc/feed.rss ${WK_DIR}/arc/feed.bak ; fi
cd ${WK_DIR}
${PYTHON_PATH} ${PY_DL_SCRIPT} ${PY_DL_CONF}.conf > ${LOG_NAME} 2>&1
for SUB_DIR in a b y z
do
	if [ -d trg/${SUB_DIR}_bak ] ; then rm -f trg/${SUB_DIR}_bak; fi
	if [ -d trg/${SUB_DIR} ] ; then mv trg/${SUB_DIR} trg/${SUB_DIR}_bak; fi
	mkdir trg/${SUB_DIR}
	if [ -f ${WK_DIR}/arc/feed.rss ] ; then mv -f ${WK_DIR}/arc/feed.rss ${WK_DIR}/arc/feed.bak ; fi
	${PYTHON_PATH} ${PY_DL_SCRIPT} ${PY_DL_CONF}_${SUB_DIR}.conf >> ${LOG_NAME} 2>&1
done
for ARC_URL in `cat ${LOG_NAME} |grep "http://.*/uc_" |sed 's|.*\(http://.*\)/uc_|\1/ar_|g'`
do
	ARC_NAME=`echo "${ARC_URL}" |sed -e 's|.*/||g' -e 's/-.*\.zip/\.zip/g'`
	${CURL_PATH} ${ARC_URL} > ${WK_DIR}/arc/${ARC_NAME} 2>/dev/null
	${UNZIP_PATH} ${WK_DIR}/arc/${ARC_NAME} -d ${WK_DIR}/trg >> ${LOG_NAME} 2>&1
done

cd ${WK_DIR}/trg

{

nkf -Sw8X < KEN_ALL.CSV  | sed -e 's/〜/～/g' > test-KEN_ALL.CSV
nkf -Sw8X < JIGYOSYO.CSV | sed -e 's/〜/～/g' > test-JIGYOSYO.CSV
nkf -Ww8X < uc_k.csv > test-uc_k.csv
nkf -Ww8X < uc_j.csv > test-uc_j.csv

echo uc_k.csv
if diff -q test-uc_k.csv test-KEN_ALL.CSV  ; then echo OK ; else echo NG ; fi

echo uc_j.csv
if diff -q test-uc_j.csv test-JIGYOSYO.CSV ; then echo OK ; else echo NG ; fi
cat uc_k.csv | sed -e 's/\"*,\"*/\t/g' -e 's/\r//' > test-uc_k.txt
cat uc_j.csv | sed -e 's/\"*,\"*/\t/g' -e 's/\r//' > test-uc_j.txt

echo t1_k.txt
if diff -q t1_k.txt test-uc_k.txt ; then echo OK ; else echo NG ; fi
echo t1_j.txt
if diff -q t1_j.txt test-uc_j.txt ; then echo OK ; else echo NG ; fi

echo t2_k.txt
mv ${LOG_DIR}/diff-t1_k-t2_k.txt ${LOG_DIR}/diff-t1_k-t2_k.bak
diff t1_k.txt t2_k.txt > ${LOG_DIR}/diff-t1_k-t2_k.txt
if diff -q ${LOG_DIR}/diff-t1_k-t2_k.bak ${LOG_DIR}/diff-t1_k-t2_k.txt ; then echo OK ; else echo NG ; fi
echo "see: diff-t1_k-t2_k.txt"

echo t2_j.txt
if diff -q t1_j.txt t2_j.txt ; then echo OK ; else echo NG ; fi
cat t2_k.txt \
	|awk -F\t -v 'OFS=\t' '{print $1, $3, $9, "", "", "", $6, "", "", $10, $11, $12, $13, $14, $15, "", ""}' \
	|sed -e 's/（\([^）]*\)）\t/\t\1/' \
	|sed -e 's/(\([^)]*\))\t/\t\1/' \
	|sed -e 's/\t\(以下に掲載がない場合\|[^\t]*一円\)\t\t\t\t[^\t]*/\t\t\t\t\1\t/' \
	|sed -e 's/\t\([^\t]*その他[^\t]*\|[^\t]*除く[^\t]*\|[^\t]*以上[^\t]*\|[^\t]*無番地[^\t]*\|丁目\|番地\)\t\t\t\([^\t]*\)\t[^\t]*/\t\t\t\1\t\2\t/' \
	> test-t2_k.txt
cat t2_j.txt \
	|awk -F\t -v 'OFS=\t' '{print $1, $8, $6, $7, $3, "", "", "", $2, $12, "", "", "", $13, "", $11, $10}' \
	> test-t2_j.txt

echo t3_k.txt
mv ${LOG_DIR}/diff-t2_k-t3_k.txt ${LOG_DIR}/diff-t2_k-t3_k.bak
diff test-t2_k.txt t3_k.txt > ${LOG_DIR}/diff-t2_k-t3_k.txt
if diff -q ${LOG_DIR}/diff-t2_k-t3_k.bak ${LOG_DIR}/diff-t2_k-t3_k.txt ; then echo OK ; else echo NG ; fi
echo "see: diff-t2_k-t3_k.txt"

echo t3_j.txt
if diff -q t3_j.txt test-t2_j.txt ; then echo OK ; else echo NG ; fi

echo tp_k.txt
cat t2_k.txt |awk -F\t -v 'OFS=\t' '{print $1, $7, $4}' |sed 's/^\(..\).../\1/g' |sort |uniq > test-tp_k.txt
if diff -q test-tp_k.txt tp_k.txt ; then echo OK ; else echo NG ; fi

echo tp_j.txt
cat t2_j.txt |awk -F\t -v 'OFS=\t' '{print $1, $4, ""}' |sed 's/^\(..\).../\1/g' |sort |uniq > test-tp_j.txt
if diff -q test-tp_j.txt tp_j.txt ; then echo OK ; else echo NG ; fi

echo tc_k.txt
cat t2_k.txt |awk -F\t -v 'OFS=\t' '{print $1, $8, $5}' |sort |uniq > test-tc_k.txt
if diff -q test-tc_k.txt tc_k.txt ; then echo OK ; else echo NG ; fi

echo tc_j.txt
cat t2_j.txt |awk -F\t -v 'OFS=\t' '{print $1, $5, ""}' |sort |uniq > test-tc_j.txt
mv ${LOG_DIR}/diff-tc_j.txt ${LOG_DIR}/diff-tc_j.bak
diff test-tc_j.txt tc_j.txt > ${LOG_DIR}/diff-tc_j.txt
if diff -q ${LOG_DIR}/diff-tc_j.bak ${LOG_DIR}/diff-tc_j.txt ; then echo OK ; else echo NG ; fi
echo "see: diff-tc_j.txt"

${PYTHON_PATH} ${JSON_CHECKER} . > /dev/null

} >> ${LOG_NAME} 2>&1
