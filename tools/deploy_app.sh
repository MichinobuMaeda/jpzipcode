#!/bin/sh
appcfg.py \
 update \
 $( dirname "$0" )/../src/gae
