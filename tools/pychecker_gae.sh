#!/bin/sh
cd $( dirname "$0" )/../src/gae
pychecker --only *.py */*.py */*/*.py */*/*/*.py
