#!/bin/sh
cd $( dirname "$0" )/../src/download
pychecker --only *.py */*.py */*/*.py */*/*/*.py
