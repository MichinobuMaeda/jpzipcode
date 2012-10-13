#!/bin/sh
dev_appserver.py \
 --admin_console_server= \
 --port=8080 \
 --high_replication \
 --clear_datastore \
 $( dirname "$0" )/../src/gae
