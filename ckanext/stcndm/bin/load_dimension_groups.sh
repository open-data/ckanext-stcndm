#!/usr/bin/env bash
python massage_dimension_groups.py | \
#  jq '.' # | \
  ckanapi load datasets $@
