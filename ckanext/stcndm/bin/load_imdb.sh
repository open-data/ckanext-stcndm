#!/usr/bin/env bash
python massage_imdb.py | \
#  jq '.' | \
  ckanapi load datasets $@
