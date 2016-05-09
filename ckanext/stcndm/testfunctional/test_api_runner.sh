#!/usr/bin/env bash

function usage() {
    echo "Usage: ${0} [<virtual-env-home>]"
    echo "(specify <virtual-env-home> directory to launch from outside active virtual environment)"
}

if [ "$#" -ne 0 ] && [ "$#" -ne 1 ]
then
    $(usage)
    exit 1
fi

# Test Variables
ckan_user="test"
ckan_password="test"
venv="${VIRTUAL_ENV}"

if [[ "${venv}" == "" ]]
then
    venv=$(echo "${1:-$HOME/stcndm/venv}" | sed 's:/*$::')
    if [[ -f "${venv}/bin/activate" ]]
    then
        source "${venv}/bin/activate"
    else
        $(usage)
        exit 1
    fi
fi

export ckan_user=${ckan_user}
export ckan_password=${ckan_password}
kill_it=0

# Initialize Database and load test data
paster --plugin=ckan db init --config=/etc/ckan/stcndm/test-core.ini
ckanapi action organization_create name=statcan title="Statistics Canada" -c /etc/ckan/stcndm/test-core.ini
paster --plugin=ckan user add ${ckan_user} email=test@canada.ca password=${ckan_password} --config=/etc/ckan/stcndm/test-core.ini
paster --plugin=ckan sysadmin add test --config=/etc/ckan/stcndm/test-core.ini
ckanapi load datasets -I stcndm_test_data.jsonl -c /etc/ckan/stcndm/test-core.ini
ckan_api=`paster --plugin=ckan user ${ckan_user} -c /etc/ckan/stcndm/test-core.ini | awk -F' ' '{ print substr($8,8) }' | awk 'NF >0' `
export ckan_api=${ckan_api}

if [[ "0" == "$(ps -ef | grep -v grep | grep 'paster serve /etc/ckan/stcndm/test-core.ini' | wc -l)" ]]
then
    # Start CKAN using test DB
    kill_it=1
    paster serve /etc/ckan/stcndm/test-core.ini --daemon
    while [[ "0" == "$(ps -ef | grep -v grep | grep 'paster serve /etc/ckan/stcndm/test-core.ini' | wc -l)" ]]
    do
        sleep 5
    done
    echo "Started CKAN service"
else
    echo "Using existing CKAN service"
fi

nosetests --ckan --with-pylons=/etc/ckan/stcndm/test-core.ini test_api.py:TestAPI

if [[ "${kill_it}" == "1" ]]
then
    # Kill CKAN server
    pasterpid="paster.pid"
    kill -9 $(<"$pasterpid")
fi

# Clean Database
paster --plugin=ckan db clean --config=/etc/ckan/stcndm/test-core.ini

if [[ "${kill_it}" == "1" ]]
then
    # Remove Paster files
    rm paster.log
    rm paster.pid
fi
