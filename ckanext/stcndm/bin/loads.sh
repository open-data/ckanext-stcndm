#!/usr/bin/env bash

cd ~/stcndm-env/ckanext-stcndm/ckanext/stcndm/bin

echo codesets > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/codesets.jsonl 2>&1 >/dev/null | grep -i error > jsonl_dumps/load_errs.txt

echo geolevels > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/geolevels.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo subjects > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/subjects.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo surveys > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/surveys.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo geodescriptors > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/geodescriptors.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo provinces > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/provinces.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo cubes > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/cubes.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo views > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/views.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo indicators > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/indicators.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo daily > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/daily.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo conferences > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/conferences.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo services > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/services.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo pumfs > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/pumfs.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo analyticals > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
ckanapi load datasets -I jsonl_dumps/analyticals.jsonl 2>&1 >/dev/null | grep -i error >> jsonl_dumps/load_errs.txt

echo rebuild search index > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt
paster --plugin=ckan search-index rebuild -r -e
echo done > jsonl_dumps/load_errs.txt
date > jsonl_dumps/load_errs.txt

