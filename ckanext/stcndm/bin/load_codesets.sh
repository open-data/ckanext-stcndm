#!/bin/bash
# convert to json lines
# add the required dataset type

curl http://localhost:8983/solr/ndm/query?q=organization:tmshortlist\&rows=200 | \
  jq '.response.docs' | \
  python massage_codesets.py | \
  jq .[] -c | \
    ckanapi load datasets $@
#  less

