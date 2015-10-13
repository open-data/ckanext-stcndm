#/bin/bash
cd ~/stcndm-env/ckanext-stcndm/ckanext/stcndm/bin
echo codesets
python massage_codesets.py > jsonl_dumps/codesets.jsonl
echo subjects
python massage_subjects.py > jsonl_dumps/subjects.jsonl
echo surveys
python massage_surveys.py > jsonl_dumps/surveys.jsonl
echo geodescriptors
python massage_geodescriptors.py > jsonl_dumps/geodescriptors.jsonl
echo cubes
python massage_cubes.py > jsonl_dumps/cubes.jsonl
echo views
python massage_views.py > jsonl_dumps/views.jsonl
echo indicators
python massage_indicators.py > jsonl_dumps/indicators.jsonl
echo daily
python massage_daily.py > jsonl_dumps/daily.jsonl
echo conferences
python massage_conferences.py > jsonl_dumps/conferences.jsonl
echo services
python massage_services.py > jsonl_dumps/services.jsonl
echo pumfs
python massage_pumfs.py > jsonl_dumps/pumfs.jsonl
echo analyticals
python massage_analyticals.py > jsonl_dumps/analyticals.jsonl

