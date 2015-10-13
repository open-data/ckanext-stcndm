#/bin/bash
cd ~/stcndm-env/ckanext-stcndm/ckanext/stcndm/bin
echo codesets
date
ckanapi load datasets -I jsonl_dumps/codesets.jsonl
echo geolevels
date
ckanapi load datasets -I jsonl_dumps/geolevels.jsonl
echo subjects
date
ckanapi load datasets -I jsonl_dumps/subjects.jsonl
echo surveys
date
ckanapi load datasets -I jsonl_dumps/surveys.jsonl
echo geodescriptors
date
ckanapi load datasets -I jsonl_dumps/geodescriptors.jsonl
echo cubes
date
ckanapi load datasets -I jsonl_dumps/cubes.jsonl
echo views
date
ckanapi load datasets -I jsonl_dumps/views.jsonl
echo indicators
date
ckanapi load datasets -I jsonl_dumps/indicators.jsonl
echo daily
date
ckanapi load datasets -I jsonl_dumps/daily.jsonl
echo conferences
date
ckanapi load datasets -I jsonl_dumps/conferences.jsonl
echo services
date
ckanapi load datasets -I jsonl_dumps/services.jsonl
echo pumfs
date
ckanapi load datasets -I jsonl_dumps/pumfs.jsonl
echo analyticals
date
ckanapi load datasets -I jsonl_dumps/analyticals.jsonl
echo provinces
date
ckanapi load datasets -I jsonl_dumps/provinces.jsonl
echo rebuild search index
date
paster --plugin=ckan search-index rebuild -r -e
echo done
date

