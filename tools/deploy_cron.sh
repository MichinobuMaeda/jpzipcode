#!/bin/sh
appcfg.py \
 update_cron \
 $( dirname "$0" )/../src/gae
