import sys
import json
import ckanapi

__author__ = 'marc'

rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj')
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='organization:corrections AND -pkuniqueidcode_bi_strs:issue*',
        rows=1000,
        start=i*1000)
    n = query_results['count'] / 1000.0
    i += 1

    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        correction_out = {
            u'owner_org': u'statcan',
            u'private': False,
            u'type': u'correction'}

        if 'correcdate_bi_strm' in line and line['correcdate_bi_strm']:
            correction_out['correction_date'] = line['correcdate_bi_strm']

        if 'correcimplevelcode_bi_strs' in line and line['correcimplevelcode_bi_strs']:
            correction_out['correction_impact_level_code'] = line['correcimplevelcode_bi_strs']

        temp = {}
        if 'correcnote_en_txtm' in line and line['correcnote_en_txtm']:
            temp['en'] = line['correcnote_en_txtm']
        if 'correcnote_fr_txtm' in line and line['correcnote_fr_txtm']:
            temp['fr'] = line['correcnote_fr_txtm']
        if temp:
            correction_out['notes'] = temp

        if 'correctionid_bi_strm' in line and line['correctionid_bi_strm']:
            correction_out['correction_id'] = line['correctionid_bi_strm']

        if 'correctypecode_bi_txtm' in line and line['correctypecode_bi_txtm']:
            correction_out['correction_type_code'] = line['correctypecode_bi_txtm']

        if 'formatcode_bi_txtm' in line and line['formatcode_bi_txtm']:
            correction_out['format_code'] = line['formatcode_bi_txtm']

        if 'pkuniqueidcode_bi_strs' in line and line['pkuniqueidcode_bi_strs']:
            id_length = line['pkuniqueidcode_bi_strs'].rfind('_')
            correction_out['corrected_product'] = line['pkuniqueidcode_bi_strs'][:id_length]

        if 'productidnew_bi_strs' in line and line['productidnew_bi_strs']:
            if len(line['productidnew_bi_strs']) == 15:
                correction_out['product_id_new'] = line['productidnew_bi_strs']
            else:
                if line['productidnew_bi_strs'].startswith('article'):
                    correction_out['product_id_new'] = line['productidnew_bi_strs'][7:26]
                else:
                    correction_out['product_id_new'] = line['pkuniqueidcode_bi_strs'][5:20]
                sys.stderr.write('incorrect productidnew {product_id} for dataset {name} set to {fixed}\n'.format(
                    product_id=line['productidnew_bi_strs'],
                    name=line['name'],
                    fixed=correction_out['product_id_new']
                ))

        print json.dumps(correction_out)
