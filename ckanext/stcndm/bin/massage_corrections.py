import sys
import json
import ckanapi

__author__ = 'marc'

correction_dict = {}

rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj')
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='organization:corrections',  # AND -pkuniqueidcode_bi_strs:issue*',
        sort='productidnew_bi_strs ASC',
        rows=1000,
        start=i*1000)
    n = query_results['count'] / 1000.0
    i += 1

    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        correction_id = line.get('correctionid_bi_strm')
        if not correction_id:
            sys.stderr.write('Correction missing ID: {line}\n'.format(
                line=line
            ))
            continue
        if correction_id not in correction_dict:
            correction_dict[correction_id] = {}
        correction_dict[correction_id]['correction_date'] = \
            line.get('correcdate_bi_strm')
        correction_dict[correction_id]['correction_impact_level_code'] = \
            line.get('correcimplevelcode_bi_strs')[:1]
        correction_dict[correction_id]['correction_type_code'] = \
            line.get('correctypecode_bi_txtm')
        product_id_new = line.get('productidnew_bi_strs')
        correction_dict[correction_id]['product_id_new'] = \
            product_id_new[7:].upper() \
                if product_id_new.startswith('article') else product_id_new.upper()
        correction_dict[correction_id]['notes'] = {
            u'en': line.get('correcnote_en_txtm'),
            u'fr': line.get('correcnote_fr_txtm')
        }
        if 'format_codes' not in correction_dict[correction_id]:
            correction_dict[correction_id]['format_codes'] = []
        correction_dict[correction_id]['format_codes'].append(
            line.get('formatcode_bi_txtm')
        )

    for correction_id in correction_dict:
        dict_out = {
            u'owner_org': u'statcan',
            u'private': False,
            u'type': u'correction',
            u'correction_id': correction_id
        }
        dict_out.update(correction_dict[correction_id])
        print json.dumps(dict_out)

