#!/usr/bin/env bash
python massage_views.py | \
  ckanapi load datasets $@
