#!/usr/bin/env bash
python massage_dimension_members.py | \
#  jq '.' # | \
  ckanapi load datasets $@
