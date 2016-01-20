#!/usr/bin/env bash

cd ~/stcndm-env/ckanext-stcndm/ckanext/stcndm/bin
echo users | tee jsonl_dumps/dump_errs.txt
python massage_users.py > jsonl_dumps/ckan_users.jsonl 2>> jsonl_dumps/dump_errs.txt
echo codesets | tee -a jsonl_dumps/dump_errs.txt
python massage_codesets.py > jsonl_dumps/codesets.jsonl 2>> jsonl_dumps/dump_errs.txt
echo subjects | tee -a jsonl_dumps/dump_errs.txt
python massage_subjects.py > jsonl_dumps/subjects.jsonl 2>> jsonl_dumps/dump_errs.txt
echo provinces | tee -a jsonl_dumps/dump_errs.txt
python massage_provinces.py > jsonl_dumps/provinces.jsonl  2>> jsonl_dumps/dump_errs.txt
echo geodescriptors | tee -a jsonl_dumps/dump_errs.txt
python massage_geodescriptors.py > jsonl_dumps/geodescriptors.jsonl 2>> jsonl_dumps/dump_errs.txt
echo surveys | tee -a jsonl_dumps/dump_errs.txt
python massage_surveys.py > jsonl_dumps/surveys.jsonl 2>> jsonl_dumps/dump_errs.txt
less echo cubes | tee -a jsonl_dumps/dump_errs.txt
python massage_cubes.py > jsonl_dumps/cubes.jsonl 2>> jsonl_dumps/dump_errs.txt
echo views | tee -a jsonl_dumps/dump_errs.txt
python massage_views.py > jsonl_dumps/views.jsonl 2>> jsonl_dumps/dump_errs.txt
echo indicators | tee -a jsonl_dumps/dump_errs.txt
python massage_indicators.py > jsonl_dumps/indicators.jsonl 2>> jsonl_dumps/dump_errs.txt
echo conferences | tee -a jsonl_dumps/dump_errs.txt
python massage_conferences.py > jsonl_dumps/conferences.jsonl 2>> jsonl_dumps/dump_errs.txt
echo services | tee -a jsonl_dumps/dump_errs.txt
python massage_services.py > jsonl_dumps/services.jsonl 2>> jsonl_dumps/dump_errs.txt
echo pumfs | tee -a jsonl_dumps/dump_errs.txt
python massage_pumfs.py > jsonl_dumps/pumfs.jsonl 2>> jsonl_dumps/dump_errs.txt
echo analyticals | tee -a jsonl_dumps/dump_errs.txt
python massage_analyticals.py > jsonl_dumps/analyticals.jsonl 2>> jsonl_dumps/dump_errs.txt
echo corrections | tee -a jsonl_dumps/dump_errs.txt
python massage_corrections.py > jsonl_dumps/corrections.jsonl 2>> jsonl_dumps/dump_errs.txt
