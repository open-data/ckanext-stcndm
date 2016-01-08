#!/usr/bin/env bash

# Test Variables
ckan_user="test"
ckan_password="test"

export ckan_user=$ckan_user
export ckan_password=$ckan_password

# Initialize Database and load test data
paster --plugin=ckan db init --config=/etc/ckan/stcndm/test-core.ini
ckanapi action organization_create name=statcan title="Statistics Canada" -c /etc/ckan/stcndm/test-core.ini
paster --plugin=ckan user add $ckan_user email=test@canada.ca password=$ckan_password --config=/etc/ckan/stcndm/test-core.ini
paster --plugin=ckan sysadmin add test --config=/etc/ckan/stcndm/test-core.ini
ckanapi load datasets -I stcndm_test_data.jsonl -c /etc/ckan/stcndm/test-core.ini
ckan_api=`paster --plugin=ckan user test -c /etc/ckan/stcndm/test-core.ini | awk -F' ' '{ print substr($8,8) }' | awk 'NF >0' `
export ckan_api=$ckan_api

# Start CKAN using test DB
paster serve /etc/ckan/stcndm/test-core.ini --daemon
sleep 8
nosetests --ckan --with-pylons=/etc/ckan/stcndm/test-core.ini

# Kill CKAN server
pasterpid="paster.pid"
kill -9 $(<"$pasterpid")

# Clean Database
paster --plugin=ckan db clean --config=/etc/ckan/stcndm/test-core.ini

# Remove Paster files
rm paster.log
rm paster.pid