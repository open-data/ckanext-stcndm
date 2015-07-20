curl http://localhost:8983/solr/ndm/query?q=organization:$1\&rows=1000 | \
  jq '.response.docs' | \
  jq 'map(keys)' | \
  jq 'reduce .[] as $i ([];.+$i)' | \
  jq 'unique'