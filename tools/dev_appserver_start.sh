#!/bin/sh
dev_appserver.py \
 --admin_console_server= \
 --port=8080 \
 --high_replication \
 $( dirname "$0" )/../src/gae
