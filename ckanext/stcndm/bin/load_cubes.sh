#!/usr/bin/env bash
python massage_cubes.py | \
  ckanapi load datasets $@
