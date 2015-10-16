#!/usr/bin/env bash

cd ~/stcndm-env/ckanext-stcndm/ckanext/stcndm/bin
echo codesets > jsonl_dumps/dump_errs.txt
python massage_codesets.py > jsonl_dumps/codesets.jsonl 2> jsonl_dumps/dump_errs.txt
echo subjects > jsonl_dumps/dump_errs.txt
python massage_subjects.py > jsonl_dumps/subjects.jsonl 2>> jsonl_dumps/dump_errs.txt
echo surveys > jsonl_dumps/dump_errs.txt
python massage_surveys.py > jsonl_dumps/surveys.jsonl 2>> jsonl_dumps/dump_errs.txt
echo geodescriptors > jsonl_dumps/dump_errs.txt
python massage_geodescriptors.py > jsonl_dumps/geodescriptors.jsonl 2>> jsonl_dumps/dump_errs.txt
echo provinces > jsonl_dumps/dump_errs.txt
python massage_provinces.py > jsonl_dumps/provinces.jsonl  2>> jsonl_dumps/dump_errs.txt
echo cubes > jsonl_dumps/dump_errs.txt
python massage_cubes.py > jsonl_dumps/cubes.jsonl 2>> jsonl_dumps/dump_errs.txt
echo views > jsonl_dumps/dump_errs.txt
python massage_views.py > jsonl_dumps/views.jsonl 2>> jsonl_dumps/dump_errs.txt
echo indicators > jsonl_dumps/dump_errs.txt
python massage_indicators.py > jsonl_dumps/indicators.jsonl 2>> jsonl_dumps/dump_errs.txt
echo daily > jsonl_dumps/dump_errs.txt
python massage_daily.py > jsonl_dumps/daily.jsonl 2>> jsonl_dumps/dump_errs.txt
echo conferences > jsonl_dumps/dump_errs.txt
python massage_conferences.py > jsonl_dumps/conferences.jsonl 2>> jsonl_dumps/dump_errs.txt
echo services > jsonl_dumps/dump_errs.txt
python massage_services.py > jsonl_dumps/services.jsonl 2>> jsonl_dumps/dump_errs.txt
echo pumfs > jsonl_dumps/dump_errs.txt
python massage_pumfs.py > jsonl_dumps/pumfs.jsonl 2>> jsonl_dumps/dump_errs.txt
echo analyticals > jsonl_dumps/dump_errs.txt
python massage_analyticals.py > jsonl_dumps/analyticals.jsonl 2>> jsonl_dumps/dump_errs.txt
