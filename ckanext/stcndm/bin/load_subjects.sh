#!/usr/bin/env bash
python massage_subject.py  | \
  jq .[] -c | \
  ckanapi load datasets $@
