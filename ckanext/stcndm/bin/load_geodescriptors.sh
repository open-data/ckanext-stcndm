#!/usr/bin/env bash
python massage_geodescriptors.py | \
#  jq '.' # | \
  ckanapi load datasets $@
