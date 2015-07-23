#!/usr/bin/env bash
curl http://ndmckanq1.stcpaz.statcan.gc.ca:8282/solr/#/ndm_core_dev/query?q=organization:tmtaxonomy\&rows=70000\&fl=tmtaxsubj_en_tmtxtm,tmtaxsubj_fr_tmtxtm,tmtaxsubjcode_bi_tmtxtm,tmtaxdisp_en_tmtxtm,tmtaxadminnotes_bi_tmtxts,tmtaxsubjoldcode_bi_tmtxtm,tmtaxatozalias_en_tmtxtm,tmtaxatozalias_fr_tmtxtm | \
  jq '.response.docs'  | \
  python massage_subject.py  | \
  jq .[] -c | \
  ckanapi load datasets $@
