#!/usr/bin/env bash
curl http://localhost:8983/solr/ndm/query?q=organization:maimdb\&rows=70000 | \
  jq '.response.docs' | \
  python massage_imdb.py | \
#  jq '.' | \
  ckanapi load datasets $@
