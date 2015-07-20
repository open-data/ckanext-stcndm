#!/bin/sh
die () {
    echo >&2 "$@"
    exit 1
}

[ "$#" -eq 2 ] || die "2 arguments required, $# provided. arg1: organisation, arg2: field name"

curl http://localhost:8983/solr/ndm/query?q=organization:$1\&rows=70000\&fl=$2 | \
   jq '.response.docs' | \
   jq "[.[].$2]" | \
   jq 'unique'
