#!/bin/sh
WK_DIR="`pwd`/$( dirname "$0" )/../test/wk/download"
JSON_CHECKER="`pwd`/$( dirname "$0" )/json_files_checker.py"
if [ -d ${WK_DIR} ] ; then rm -rf ${WK_DIR} ; fi
mkdir -p ${WK_DIR}
cd ${WK_DIR}
for FILENAME in \
	arch_ken-20120827 \
	utf8_ken-20120827 \
	tsv1_ken-20120827 \
	tsv2_ken-20120827 \
	tsv3_ken-20120827 \
	json_ken-20120827 \
	arch_jig-20120829 \
	utf8_jig-20120829 \
	tsv1_jig-20120829 \
	tsv2_jig-20120829 \
	tsv3_jig-20120829 \
	json_jig-20120829
do
	echo ${FILENAME}.zip
	if wget -q http://localhost:8080/download/${FILENAME}.zip ; then echo OK ; else echo NG ; fi
	if unzip -q ${FILENAME} ; then echo OK ; else echo NG ; fi
done
wget -q http://localhost:8080/feed.rss
sha1sum arch_ken-20120827.zip
ls -l   arch_ken-20120827.zip
ls -l   KEN_ALL.CSV
sha1sum utf8_ken-20120827.zip
ls -l   utf8_ken-20120827.zip
ls -l   utf8_ken.csv
sha1sum tsv1_ken-20120827.zip
ls -l   tsv1_ken-20120827.zip
ls -l   tsv1_ken.txt
sha1sum tsv2_ken-20120827.zip
ls -l   tsv2_ken-20120827.zip
ls -l   tsv2_ken.txt
sha1sum tsv3_ken-20120827.zip
ls -l   tsv3_ken-20120827.zip
ls -l   tsvp_ken.txt
ls -l   tsvc_ken.txt
ls -l   tsv3_ken.txt
sha1sum json_ken-20120827.zip
ls -l   json_ken-20120827.zip
sha1sum arch_jig-20120829.zip
ls -l   arch_jig-20120829.zip
ls -l   JIGYOSYO.CSV
sha1sum utf8_jig-20120829.zip
ls -l   utf8_jig-20120829.zip
ls -l   utf8_jig.csv
sha1sum tsv1_jig-20120829.zip
ls -l   tsv1_jig-20120829.zip
ls -l   tsv1_jig.txt
sha1sum tsv2_jig-20120829.zip
ls -l   tsv2_jig-20120829.zip
ls -l   tsv2_jig.txt
sha1sum tsv3_jig-20120829.zip
ls -l   tsv3_jig-20120829.zip
ls -l   tsvp_jig.txt
ls -l   tsvc_jig.txt
ls -l   tsv3_jig.txt
sha1sum json_jig-20120829.zip
ls -l   json_jig-20120829.zip
nkf -Sw8X < KEN_ALL.CSV  | perl -ne 's/〜/～/g; print' > test-KEN_ALL.CSV
nkf -Sw8X < JIGYOSYO.CSV | perl -ne 's/〜/～/g; print' > test-JIGYOSYO.CSV
nkf -Ww8X < utf8_ken.csv > test-utf8_ken.csv
nkf -Ww8X < utf8_jig.csv > test-utf8_jig.csv
echo utf8_ken.csv
if diff -q test-utf8_ken.csv test-KEN_ALL.CSV  ; then echo OK ; else echo NG ; fi
echo utf8_jig.csv
if diff -q test-utf8_jig.csv test-JIGYOSYO.CSV ; then echo OK ; else echo NG ; fi
cat utf8_ken.csv | perl -ne 's/\"*,\"*/\t/g; s/\r//; print' > test-utf8_ken.txt
cat utf8_jig.csv | perl -ne 's/\"*,\"*/\t/g; s/\r//; print' > test-utf8_jig.txt
echo tsv1_ken.txt
if diff -q tsv1_ken.txt test-utf8_ken.txt ; then echo OK ; else echo NG ; fi
echo tsv1_jig.txt
if diff -q tsv1_jig.txt test-utf8_jig.txt ; then echo OK ; else echo NG ; fi
echo tsv2_ken.txt
diff tsv1_ken.txt tsv2_ken.txt > diff-tsv1_ken-tsv2_ken.txt
echo "see: diff-tsv1_ken-tsv2_ken.txt"
echo tsv2_jig.txt
if diff -q tsv1_jig.txt tsv2_jig.txt ; then echo OK ; else echo NG ; fi
cat tsv2_ken.txt \
	|perl -ne 's/^([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t/$1\t$3\t$9\t\t\t\t$6\t\t\t/; print' \
	|perl -ne 'chomp; s/$/\t\t\n/; print $_' \
	|perl -ne 's/([^\t]*)（([^\t]*)）\t\t/$1\t$2\t/; print' \
	|perl -ne 's/([^\t]*)\(([^\t]*)\)\t\t/$1\t$2\t/; print' \
	|perl -ne 's/\t(以下に掲載がない場合|[^\t]*一円)\t\t\t\t[^\t]*/\t\t\t\t$1\t/; print' \
	|perl -ne 's/\t([^\t]*その他[^\t]*|[^\t]*除く[^\t]*|[^\t]*以上[^\t]*|[^\t]*無番地[^\t]*|丁目|番地)\t\t\t([^\t]*)\t[^\t]*/\t\t\t$1\t$2\t/; print' \
	> test-tsv2_ken.txt
cat tsv2_jig.txt \
	|perl -ne 's/^([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t/$1\t$8\t$6\t$7\t$3\t\t\t\t$2\t/; print' \
	|perl -ne 'chomp; s/\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)$/\t$3\t\t\t\t$4\t\t$2\t$1\n/; print' \
	> test-tsv2_jig.txt
echo tsv3_ken.txt
diff test-tsv2_ken.txt tsv3_ken.txt > diff-tsv2_ken-tsv3_ken.txt
echo "see: diff-tsv2_ken-tsv3_ken.txt"
echo tsv3_jig.txt
if diff -q tsv3_jig.txt test-tsv2_jig.txt ; then echo OK ; else echo NG ; fi
echo tsvp_ken.txt
cat tsv2_ken.txt \
	|perl -ne 's/^(..)...\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t.*/$1\t$7\t$4/; print' \
	|uniq \
	> test-tsvp_ken.txt
if diff -q test-tsvp_ken.txt tsvp_ken.txt ; then echo OK ; else echo NG ; fi
echo tsvp_jig.txt
cat tsv2_jig.txt \
	|perl -ne 's/^(..)...\t([^\t]*)\t([^\t]*)\t([^\t]*)\t.*/$1\t$4\t/; print' \
	|uniq \
	> test-tsvp_jig.txt
if diff -q test-tsvp_jig.txt tsvp_jig.txt ; then echo OK ; else echo NG ; fi
echo tsvc_ken.txt
cat tsv2_ken.txt \
	|perl -ne 's/^([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t.*/$1\t$8\t$5/; print' \
	|uniq \
	> test-tsvc_ken.txt
if diff -q test-tsvc_ken.txt tsvc_ken.txt ; then echo OK ; else echo NG ; fi
echo tsvc_jig.txt
cat tsv2_jig.txt \
	|perl -ne 's/^([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t([^\t]*)\t.*/$1\t$5\t/; print' \
	|uniq \
	> test-tsvc_jig.txt
diff test-tsvc_jig.txt tsvc_jig.txt > diff-tsvc_jig.txt
echo "see: diff-tsvc_jig.txt"
/usr/bin/python ${JSON_CHECKER} . > json_checker.log
echo "see: json_checker.log"
