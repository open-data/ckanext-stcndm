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
code_count = {}
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

        line_out_codeset = {
            'owner_org': u'statcan',
            'private': False,
            'type': u'codeset',
            'codeset_type': u'dimension_group'}

        # if '10uid_bi_strs' in line and line['10uid_bi_strs']:
        #    line_out['product_id_old'] = line['10uid_bi_strs']

        temp = {}
        if 'tmdimentext_en_tmtxtm' in line and line['tmdimentext_en_tmtxtm']:
            temp[u'en'] = line['tmdimentext_en_tmtxtm']
        if 'tmdimentext_fr_tmtxtm' in line and line['tmdimentext_fr_tmtxtm']:
            temp[u'fr'] = line['tmdimentext_fr_tmtxtm']
        if temp:
            line_out['title'] = temp
            line_out_codeset['title'] = {
                u'en': temp['en'],
                u'fr': temp['fr']}

        if 'tmdimencode_bi_tmtxtm' in line and line['tmdimencode_bi_tmtxtm']:
            if 'tmdimenalias_bi_tmtxtm' in line and line['tmdimenalias_bi_tmtxtm']:
                if line['tmdimencode_bi_tmtxtm'] in code_count:
                    code_count[line['tmdimencode_bi_tmtxtm']].append(line['tmdimenalias_bi_tmtxtm'])
                else:
                    code_count[line['tmdimencode_bi_tmtxtm']] = [line['tmdimenalias_bi_tmtxtm']]
            line_out['dimension_group_code'] = line['tmdimencode_bi_tmtxtm']
            line_out['name'] = u'dimension_member-{0}_{1}'.format(line['tmdimencode_bi_tmtxtm'],
                                                                  len(code_count[line['tmdimencode_bi_tmtxtm']]))
            line_out_codeset['codeset_value'] = line['tmdimencode_bi_tmtxtm']
            line_out_codeset['name'] = u'dimension_group-{0}'.format(line['tmdimencode_bi_tmtxtm'])

        if 'tmdimenalias_bi_tmtxtm' in line and line['tmdimenalias_bi_tmtxtm']:
            line_out['dimension_member_alias'] = {
                u'en': line['tmdimenalias_bi_tmtxtm'],
                u'fr': line['tmdimenalias_bi_tmtxtm']}
            line_out['title'][u'en'] += ' / {0}'.format(line['tmdimenalias_bi_tmtxtm'])
            line_out['title'][u'fr'] += ' / {0}'.format(line['tmdimenalias_bi_tmtxtm'])

        # if 'title' in line and line['title']:
        #     line_out['old_title'] = {
        #         u'en': line['title'],
        #         u'fr': line['title']}

        if 'license_title' in line:
            line_out['license_title'] = line['license_title']

        if 'license_url' in line:
            line_out['license_url'] = line['license_url']

        if 'license_id' in line:
            line_out['license_id'] = line['license_id']

        if len(code_count[line['tmdimencode_bi_tmtxtm']]) == 1:
            print json.dumps(line_out_codeset)
        print json.dumps(line_out)
