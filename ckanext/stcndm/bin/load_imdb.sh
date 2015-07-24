#!/usr/bin/env bash
#curl http://ndmckanq1.stcpaz.statcan.gc.ca:8282/solr/ndm_core_dev/query?q=organization:maimdb\&rows=70000 | \
#  jq '.response.docs' | \
python massage_imdb.py | \
#  jq '.' | \
  ckanapi load datasets $@
