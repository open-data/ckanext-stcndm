__author__ = 'marc'

import json
import ckanapi


def listify(value):
    if isinstance(value, unicode):
        return filter(None, map(unicode.strip, value.split(';')))  # filter removes empty strings
    elif isinstance(value, list):
        return filter(None, map(unicode.strip, value[0].split(';')))
    else:
        return []

rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj/')
for i in range(0, 10):
    query_results = rc.action.package_search(
        q='organization:tmsgccode',
        rows=1000,
        start=i*1000)
    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        line_out = {'owner_org': u'statcan',
                    'private': False,
                    'type': u'geodescriptor'}

        if '10uid_bi_strs' in line and line['10uid_bi_strs']:
            line_out['product_id_old'] = line['10uid_bi_strs']

        temp = {}
        if 'tmsgcname_en_tmtxtm' in line and line['tmsgcname_en_tmtxtm']:
            temp[u'en'] = line['tmsgcname_en_tmtxtm']
        if 'tmsgcname_fr_tmtxtm' in line and line['tmsgcname_fr_tmtxtm']:
            temp[u'fr'] = line['tmsgcname_fr_tmtxtm']
        if temp:
            line_out['title'] = temp

        if 'tmsgcspecificcode_bi_tmtxtm' in line and line['tmsgcspecificcode_bi_tmtxtm']:
            line_out['geodescriptor_specific_code'] = line['tmsgcspecificcode_bi_tmtxtm']
            line_out['name'] = u'geodescriptor-{0}'.format(line['tmsgcspecificcode_bi_tmtxtm'].lower())

        if 'tmsgccode_bi_tmtxtm' in line and line['tmsgccode_bi_tmtxtm']:
            line_out['geolevel_code'] = line['tmsgccode_bi_tmtxtm']

        if 'title' in line and line['title']:
            line_out['old_title'] = {
                u'en': line['title'],
                u'fr': line['title']}

        print json.dumps(line_out)
