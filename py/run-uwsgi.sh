#!/bin/sh
echo `pwd`
export PTO_PAPI_SETTINGS=`pwd`/../settings.py
export PTO_PAPI_IQL_SETTINGS=`pwd`/../iql_settings.py

/usr/bin/uwsgi -s /tmp/papi.sock --manage-script-name --mount /papi=ptoweb:app --master --processes 4 --threads 2 --plugin python3

