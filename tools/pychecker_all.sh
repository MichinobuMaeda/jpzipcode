#!/bin/sh
BASE_DIR=`pwd`/$( dirname "$0" )/..
cd ${BASE_DIR}/src/gae
pychecker --only *.py */*.py */*/*.py */*/*/*.py
cd ${BASE_DIR}//src/download
pychecker --only *.py */*.py */*/*.py */*/*/*.py
