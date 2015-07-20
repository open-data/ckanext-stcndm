#!/bin/bash
# convert to json lines

cat geolevel.js | \
  jq .[] -c | \
  ckanapi load datasets $@