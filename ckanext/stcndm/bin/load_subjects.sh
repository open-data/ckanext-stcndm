curl http://localhost:8983/solr/ndm/query?q=organization:tmtaxonomy\&rows=500\&fl=tmtaxsubj_en_tmtxtm,tmtaxsubj_fr_tmtxtm,tmtaxsubjcode_bi_tmtxtm,tmtaxdisp_en_tmtxtm,tmtaxadminnotes_bi_tmtxts,tmtaxsubjoldcode_bi_tmtxtm,tmtaxatozalias_en_tmtxtm,tmtaxatozalias_fr_tmtxtm | \
  jq '.response.docs' | \
  python massage_subject.py | \
  jq .[] -c | \
  jq '.type="subject"' -c | \
  ckanapi load datasets $@
