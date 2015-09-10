#!/bin/bash
# convert to json lines
# add the required dataset type

    python massage_codesets.py | \
    ckanapi load datasets $@

ckanapi load datasets -I datasets/geolevel.jsonl 
