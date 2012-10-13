#!/bin/sh
cd $( dirname "$0" )/../test/src_arch
/usr/bin/python -m SimpleHTTPServer 8999
