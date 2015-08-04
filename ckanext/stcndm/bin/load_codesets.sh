#!/bin/bash
# convert to json lines
# add the required dataset type

    python massage_codesets.py | \
    ckanapi load datasets $@

cat geolevel.js | \
    jq .[] -c | \
    ckanapi load datasets $@
