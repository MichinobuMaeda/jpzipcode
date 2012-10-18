#!/bin/sh
TRG_SCRIPT=$( dirname "$0" )/../src/download/jpzipcode_download.py
TRG_CONF=$( dirname "$0" )/../test/jpzipcode_download.conf
WK_DIR=$( dirname "$0" )/../test/site/download
if [ -f ${WK_DIR}/arc/feed.rss ] ; then rm ${WK_DIR}/arc/feed.rss ; fi
/usr/bin/python ${TRG_SCRIPT} ${TRG_CONF}
