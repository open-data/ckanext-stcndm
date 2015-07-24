#!/bin/bash
# convert to json lines
# add the required dataset type

curl http://ndmckanq1.stcpaz.statcan.gc.ca:8282/solr/ndm_core_dev/query?q=organization:tmshortlist\&rows=70000 | \
    jq '.response.docs' | \
    python massage_codesets.py | \
    jq .[] -c | \
    ckanapi load datasets $@

cat geolevel.js | \
    jq .[] -c | \
    ckanapi load datasets $@
