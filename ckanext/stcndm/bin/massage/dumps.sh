#!/usr/bin/env bash

cd ~/stcndm-env/ckanext-stcndm/ckanext/stcndm/bin
echo users | tee logs/dump_errs.txt
python massage/massage_users.py > jsonl_dumps/ckan_users.jsonl 2>> logs/dump_errs.txt
echo codesets | tee -a logs/dump_errs.txt
python massage/massage_codesets.py > jsonl_dumps/codesets.jsonl 2>> logs/dump_errs.txt
echo subjects | tee -a logs/dump_errs.txt
python massage/massage_subjects.py > jsonl_dumps/subjects.jsonl 2>> logs/dump_errs.txt
echo provinces | tee -a logs/dump_errs.txt
python massage/massage_provinces.py > jsonl_dumps/provinces.jsonl  2>> logs/dump_errs.txt
echo geodescriptors | tee -a logs/dump_errs.txt
python massage/massage_geodescriptors.py > jsonl_dumps/geodescriptors.jsonl 2>> logs/dump_errs.txt
echo surveys | tee -a logs/dump_errs.txt
python massage/massage_surveys.py > jsonl_dumps/surveys.jsonl 2>> logs/dump_errs.txt
less echo cubes | tee -a logs/dump_errs.txt
python massage/massage_cubes.py > jsonl_dumps/cubes.jsonl 2>> logs/dump_errs.txt
echo views | tee -a logs/dump_errs.txt
python massage/massage_views.py > jsonl_dumps/views.jsonl 2>> logs/dump_errs.txt
echo indicators | tee -a logs/dump_errs.txt
python massage/massage_indicators.py > jsonl_dumps/indicators.jsonl 2>> logs/dump_errs.txt
echo conferences | tee -a logs/dump_errs.txt
python massage/massage_conferences.py > jsonl_dumps/conferences.jsonl 2>> logs/dump_errs.txt
echo services | tee -a logs/dump_errs.txt
python massage/massage_services.py > jsonl_dumps/services.jsonl 2>> logs/dump_errs.txt
echo pumfs | tee -a logs/dump_errs.txt
python massage/massage_pumfs.py > jsonl_dumps/pumfs.jsonl 2>> logs/dump_errs.txt
echo analyticals | tee -a logs/dump_errs.txt
python massage/massage_analyticals.py > jsonl_dumps/analyticals.jsonl 2>> logs/dump_errs.txt
echo corrections | tee -a logs/dump_errs.txt
python massage/massage_corrections.py > jsonl_dumps/corrections.jsonl 2>> logs/dump_errs.txt
