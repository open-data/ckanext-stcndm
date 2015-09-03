#!/usr/bin/env bash
python massage_subjects.py  | \
  jq . -c | \
  ckanapi load datasets $@
