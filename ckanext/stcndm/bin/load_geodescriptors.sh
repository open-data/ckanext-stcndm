#!/usr/bin/env bash
python massage_geodescriptors.py | \
  jq . -c  | \
  ckanapi load datasets $@
