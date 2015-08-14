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
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='organization:tmdimmlist',
        rows=1000,
        start=i*1000)
    i += 1
    n = query_results['count'] / 1000.0
    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        line_out = {'owner_org': u'statcan',
                    'private': False,
                    'type': u'dimension_member'}

        if '10uid_bi_strs' in line and line['10uid_bi_strs']:
            line_out['product_id_old'] = line['10uid_bi_strs']

        temp = {}
        if 'tmdimentext_en_tmtxtm' in line and line['tmdimentext_en_tmtxtm']:
            temp[u'en'] = line['tmdimentext_en_tmtxtm']
        if 'tmdimentext_fr_tmtxtm' in line and line['tmdimentext_fr_tmtxtm']:
            temp[u'fr'] = line['tmdimentext_fr_tmtxtm']
        if temp:
            line_out['title'] = temp

        if 'tmdimencode_bi_tmtxtm' in line and line['tmdimencode_bi_tmtxtm']:
            line_out['dimension_member_code'] = line['tmdimencode_bi_tmtxtm']
            line_out['name'] = u'dimension_member-{0}'.format(line['tmdimencode_bi_tmtxtm'])

        if 'tmdimenalias_bi_tmtxtm' in line and line['tmdimenalias_bi_tmtxtm']:
            line_out['dimension_member_alias'] = {
                u'en': line['tmdimenalias_bi_tmtxtm'],
                u'fr': line['tmdimenalias_bi_tmtxtm']}

        if 'title' in line and line['title']:
            line_out['old_title'] = {
                u'en': line['title'],
                u'fr': line['title']}

        print json.dumps(line_out)
