#!/usr/bin/env bash
curl http://localhost:8983/solr/ndm/query?q=organization:maimdb\&rows=10 | \
  jq '.response.docs' | \
  python massage_imdb.py # | \
#  jq '.'
#  jq .[] -c # | \
#  jq '.type="subject"' -c | \
#  ckanapi load datasets $@