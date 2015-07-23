#!/usr/bin/env bash
curl http://localhost:8983/solr/ndm/query?q=organization:maimdb\&rows=70000\&start=544 | \
  jq '.response.docs' | \
  python massage_imdb.py | \
#  jq '.'
#  jq . -c | \
  ckanapi load datasets $@
