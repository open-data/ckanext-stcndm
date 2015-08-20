#!/usr/bin/env bash
python massage_survey.py | \
#  jq '.' | \
  ckanapi load datasets $@
