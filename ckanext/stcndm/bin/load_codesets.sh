#!/bin/bash
# convert to json lines
# add the required dataset type

cat codesets.js | \
    jq .[] -c | \
    jq '.type="codeset"' -c | \
    ckanapi load datasets $@

