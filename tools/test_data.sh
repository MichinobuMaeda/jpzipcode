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
BASE_DIR="`pwd`/$( dirname "$0" )/.."
SRC_DIR="${BASE_DIR}/src"
TEST_DIR="${BASE_DIR}/test"
SITE_DIR="${TEST_DIR}/site"
DATA_DIR="${SITE_DIR}/data"
LOG_DIR="${TEST_DIR}/log"
LOG_NAME="${LOG_DIR}/test_data.log"
PY_DL_SCRIPT="${SRC_DIR}/download/jpzipcode_download.py"
PY_DL_CONF="${TEST_DIR}/jpzipcode_download"
JSON_CHECKER="${BASE_DIR}/tools/json_files_checker.py"
#
echo "UNZIP_PATH   ${UNZIP_PATH}"
echo "PYTHON_PATH  ${PYTHON_PATH}"
echo "CURL_PATH    ${CURL_PATH}"
echo "BASE_DIR     ${BASE_DIR}"
echo "SRC_DIR      ${SRC_DIR}"
echo "TEST_DIR     ${TEST_DIR}"
echo "SITE_DIR     ${SITE_DIR}"
echo "DATA_DIR     ${DATA_DIR}"
echo "LOG_DIR      ${LOG_DIR}"
echo "LOG_NAME     ${LOG_NAME}"
echo "PY_DL_SCRIPT ${PY_DL_SCRIPT}"
echo "PY_DL_CONF   ${PY_DL_CONF}"
echo "JSON_CHECKER ${JSON_CHECKER}"
#
if [ ! -d ${DATA_DIR} ] ; then
	mkdir -p ${DATA_DIR}
fi
if [ -f ${DATA_DIR}/arc/feed.rss ] ; then
	mv -f ${DATA_DIR}/arc/feed.rss ${DATA_DIR}/arc/feed.bak
fi
#
if [ -d ${SITE_DIR}/static ] ; then
	rm -rf ${SITE_DIR}/static
fi
mkdir -p ${SITE_DIR}/static
cp -r ${SRC_DIR}/gae/static/* ${SITE_DIR}/static
#
if [ -d ${SITE_DIR}/demo ] ; then
	rm -rf ${SITE_DIR}/demo
fi
mkdir -p ${SITE_DIR}/demo
cat ${SRC_DIR}/demo/index.html \
	|sed 's/jpzipcode\.appspot\.com/localhost:8080/g' \
	> ${SITE_DIR}/demo/index.html
#
echo "Download and unzip CSV, TSV."
${PYTHON_PATH} ${PY_DL_SCRIPT} ${PY_DL_CONF}.conf > ${LOG_NAME} 2>&1
#
cd ${DATA_DIR}/trg
#
for SUB_TYPE in a b y z
do
	echo "Download and unzip JSON:${SUB_TYPE}."
	if [ -f ${DATA_DIR}/arc/feed.rss ] ; then
		mv -f ${DATA_DIR}/arc/feed.rss ${DATA_DIR}/arc/feed.bak
	fi
	${PYTHON_PATH} ${PY_DL_SCRIPT} ${PY_DL_CONF}_${SUB_TYPE}.conf >> ${LOG_NAME} 2>&1
done
#
echo "Download and unzip JP Original Data."
for ARC_URL in `cat ${LOG_NAME} |grep "http://.*/uc_" |sed 's|.*\(http://.*\)/uc_|\1/ar_|g'`
do
	ARC_NAME=`echo "${ARC_URL}" |sed -e 's|.*/||g' -e 's/-.*\.zip/\.zip/g'`
	${CURL_PATH} ${ARC_URL} > ${DATA_DIR}/arc/${ARC_NAME} 2>/dev/null
	${UNZIP_PATH} ${DATA_DIR}/arc/${ARC_NAME} >> ${LOG_NAME} 2>&1
done
#
echo "Check CSV, TSV."
{

nkf -Sw8X < KEN_ALL.CSV  | sed -e 's/〜/～/g' > test-KEN_ALL.CSV
nkf -Sw8X < JIGYOSYO.CSV | sed -e 's/〜/～/g' > test-JIGYOSYO.CSV
nkf -Ww8X < uc_k.csv > test-uc_k.csv
nkf -Ww8X < uc_j.csv > test-uc_j.csv

echo uc_k.csv
if diff -q test-uc_k.csv test-KEN_ALL.CSV ; then
	echo OK
else
	echo NG
fi
#
echo uc_j.csv
if diff -q test-uc_j.csv test-JIGYOSYO.CSV ; then
	echo OK
else
	echo NG
fi
#
echo t1_k.txt
cat uc_k.csv | sed -e 's/\"*,\"*/\t/g' -e 's/\r//' > test-uc_k.txt
if diff -q t1_k.txt test-uc_k.txt ; then
	echo OK
else
	echo NG
fi
#
echo t1_j.txt
cat uc_j.csv | sed -e 's/\"*,\"*/\t/g' -e 's/\r//' > test-uc_j.txt
if diff -q t1_j.txt test-uc_j.txt ; then
	echo OK
else
	echo NG
fi
#
echo t2_k.txt
mv ${LOG_DIR}/diff-t1_k-t2_k.txt ${LOG_DIR}/diff-t1_k-t2_k.bak
diff t1_k.txt t2_k.txt > ${LOG_DIR}/diff-t1_k-t2_k.txt
if diff -q ${LOG_DIR}/diff-t1_k-t2_k.bak ${LOG_DIR}/diff-t1_k-t2_k.txt ; then
	echo OK
else
	echo NG
fi
echo "see: diff-t1_k-t2_k.txt"
#
echo t2_j.txt
if diff -q t1_j.txt t2_j.txt ; then
	echo OK
else
	echo NG
fi
#
echo t3_k.txt
cat t2_k.txt \
	|awk -F\t -v 'OFS=\t' '{print $1, $3, $9, "", "", "", $6, "", "", $10, $11, $12, $13, $14, $15, "", ""}' \
	|sed -e 's/（\([^）]*\)）\t/\t\1/' \
	|sed -e 's/(\([^)]*\))\t/\t\1/' \
	|sed -e 's/\t\(以下に掲載がない場合\|[^\t]*一円\)\t\t\t\t[^\t]*/\t\t\t\t\1\t/' \
	|sed -e 's/\t\([^\t]*その他[^\t]*\|[^\t]*除く[^\t]*\|[^\t]*以上[^\t]*\|[^\t]*無番地[^\t]*\|丁目\|番地\)\t\t\t\([^\t]*\)\t[^\t]*/\t\t\t\1\t\2\t/' \
	> test-t2_k.txt

mv ${LOG_DIR}/diff-t2_k-t3_k.txt ${LOG_DIR}/diff-t2_k-t3_k.bak
diff test-t2_k.txt t3_k.txt > ${LOG_DIR}/diff-t2_k-t3_k.txt
if diff -q ${LOG_DIR}/diff-t2_k-t3_k.bak ${LOG_DIR}/diff-t2_k-t3_k.txt ; then
	echo OK
else
	echo NG
fi
echo "see: diff-t2_k-t3_k.txt"
#
echo t3_j.txt
cat t2_j.txt \
	|awk -F\t -v 'OFS=\t' '{print $1, $8, $6, $7, $3, "", "", "", $2, $12, "", "", "", $13, "", $11, $10}' \
	> test-t2_j.txt
if diff -q t3_j.txt test-t2_j.txt ; then
	echo OK
else
	echo NG
fi
#
echo tp_k.txt
cat t2_k.txt \
	|awk -F\t -v 'OFS=\t' '{print $1, $7, $4}' \
	|sed 's/^\(..\).../\1/g' |sort |uniq \
	> test-tp_k.txt
if diff -q test-tp_k.txt tp_k.txt ; then
	echo OK
else
	echo NG
fi
#
echo tp_j.txt
cat t2_j.txt \
	|awk -F\t -v 'OFS=\t' '{print $1, $4, ""}' \
	|sed 's/^\(..\).../\1/g' |sort |uniq \
	> test-tp_j.txt
if diff -q test-tp_j.txt tp_j.txt ; then
	echo OK
else
	echo NG
fi
#
echo tc_k.txt
cat t2_k.txt \
	|awk -F\t -v 'OFS=\t' '{print $1, $8, $5}' |sort |uniq \
	> test-tc_k.txt
if diff -q test-tc_k.txt tc_k.txt ; then
	echo OK
else
	echo NG
fi
#
echo tc_j.txt
cat t2_j.txt \
	|awk -F\t -v 'OFS=\t' '{print $1, $5, ""}' |sort |uniq \
	> test-tc_j.txt
mv ${LOG_DIR}/diff-tc_j.txt ${LOG_DIR}/diff-tc_j.bak
diff test-tc_j.txt tc_j.txt > ${LOG_DIR}/diff-tc_j.txt
if diff -q ${LOG_DIR}/diff-tc_j.bak ${LOG_DIR}/diff-tc_j.txt ; then
	echo OK
else
	echo NG
fi
echo "see: diff-tc_j.txt"

} >> ${LOG_NAME} 2>&1
#
echo "Check JSON format."
${PYTHON_PATH} ${JSON_CHECKER} . > /dev/null 2>> ${LOG_NAME}
