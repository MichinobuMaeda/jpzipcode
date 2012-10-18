#!/bin/sh
cd $( dirname "$0" )/../test/site
/usr/bin/python -m SimpleHTTPServer 8999
