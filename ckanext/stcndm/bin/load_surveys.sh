#!/usr/bin/env bash
python massage_surveys.py | \
#  jq '.' | \
  ckanapi load datasets $@
