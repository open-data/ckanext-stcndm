#!/usr/bin/env bash
curl http://ndmckanq1.stcpaz.statcan.gc.ca:8282/solr/ndm_core_dev/query?q=organization:$1\&rows=1000 | \
  jq '.response.docs' | \
  jq 'map(keys)' | \
  jq 'reduce .[] as $i ([];.+$i)' | \
  jq 'unique'
