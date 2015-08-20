__author__ = 'marc'

import sys
import json
import yaml
import ckanapi


def listify(value):
    if isinstance(value, unicode):
        return filter(None, map(unicode.strip, value.split(';')))  # filter removes empty strings
    elif isinstance(value, list):
        return filter(None, map(unicode.strip, value[0].split(';')))
    else:
        return []


def code_lookup(old_field_name, data_set, choice_list):
    _temp = data_set[old_field_name]
    field_values = listify(_temp)
    codes = []
    for field_value in field_values:
        code = None
        for choice in choice_list:
            if choice['label']['en'].lower().strip() == field_value.lower().strip():
                if choice['value']:
                    code = choice['value']
        if not code:
            sys.stderr.write('publication-{0}: weird {1} .{2}.{3}.\n'.format(line['productidnew_bi_strs'], old_field_name, _temp, field_value))
        else:
            codes.append(code)
    return codes

rc = ckanapi.RemoteCKAN('http://127.0.0.1:5000')

content_type_list = []
geolevel_list = []
frequency_list = []
status_list = []
results = rc.action.package_search(
    q='type:codeset',
    rows=1000)
for codeset in results['results']:
    if codeset['codeset_type'] == 'content_type':
        content_type_list.append({
            'label': codeset['title'],
            'value': codeset['codeset_value']
        })
    if codeset['codeset_type'] == 'geolevel':
        geolevel_list.append({
            'label': codeset['title'],
            'value': codeset['codeset_value']
        })
    if codeset['codeset_type'] == 'frequency':
        frequency_list.append({
            'label': codeset['title'],
            'value': codeset['codeset_value']
        })
    if codeset['codeset_type'] == 'status':
        status_list.append({
            'label': codeset['title'],
            'value': codeset['codeset_value']
        })

subject_list = []
results = rc.action.package_search(
    q='type:subject',
    rows=1000)
for result in results['results']:
    subject_list.append({
        'label': result['title'],
        'value': result['subject_code']
    })

# geodescriptor_list = []
# results = rc.action.package_search(
#     q='type:geodescriptor',
#     rows=1000)
# for result in results['results']:
#     if 'geodescriptor_code' in result:
#         continue
#     geodescriptor_list.append({
#         'label': result['title'],
#         'value': result['geodescriptor_code']
#     })

dimension_member_list = []
results = rc.action.package_search(
    q='type:dimension_member',
    rows=1000)
for result in results['results']:
    if 'dimension_member_code' not in result:
        continue
    dimension_member_list.append({
        'label': result['title'],
        'value': result['dimension_member_code']
    })

# survey_source_list = []
# results = rc.action.package_search(
#     q='type:survey',
#     rows=1000)
# for result in results['results']:
#     survey_source_list.append({
#         'label': result['title'],
#         'value': result['product_id_new']
#     })

f = open('../schemas/presets.yaml')
presetMap = yaml.safe_load(f)
f.close()
for preset in presetMap['presets']:
    if preset['preset_name'] == 'ndm_archive_status':
        archive_status_list = preset['values']['choices']
        if not archive_status_list:
            raise ValueError('could not find archive status preset')
    if preset['preset_name'] == 'ndm_collection_methods':
        collection_method_list = preset['values']['choices']
        if not collection_method_list:
            raise ValueError('could not find collection method preset')
    if preset['preset_name'] == 'ndm_survey_status':
        survey_status_list = preset['values']['choices']
        if not survey_status_list:
            raise ValueError('could not find survey status preset')
    if preset['preset_name'] == 'ndm_survey_participation':
        survey_participation_list = preset['values']['choices']
        if not survey_participation_list:
            raise ValueError('could not find survey participation preset')
    if preset['preset_name'] == 'ndm_survey_owner':
        survey_owner_list = preset['values']['choices']
        if not survey_owner_list:
            raise ValueError('could not find survey owner preset')
    # if preset['preset_name'] == 'ndm_formats':
    #     format_list = preset['values']['choices']
    #     if not format_list:
    #         raise ValueError('could not find format preset')
    if preset['preset_name'] == 'ndm_tracking':
        tracking_list = preset['values']['choices']
        if not tracking_list:
            raise ValueError('could not find tracking preset')
    if preset['preset_name'] == 'ndm_display':
        display_list = preset['values']['choices']
        if not display_list:
            raise ValueError('could not find display preset')
    if preset['preset_name'] == 'ndm_publish_status':
        publish_list = preset['values']['choices']
        if not publish_list:
            raise ValueError('could not find display preset')

for i in range(0, 10):
    rc = ckanapi.RemoteCKAN('http://107.170.204.240:5000/')
    query_results = rc.action.package_search(
        q='organization:maprimary AND extras_pkuniqueidcode_bi_strs:pub*',
        rows=1000,
        start=i*1000)
    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        line_out = {u'owner_org': u'statcan',
                    u'private': False,
                    u'type': u'publication',
                    u'product_type_code': u'20'}

        temp = {}
        if 'adminnotes_bi_txts' in line and line['adminnotes_bi_txts']:
            temp[u'en'] = line['adminnotes_bi_txts']
            temp[u'fr'] = line['adminnotes_bi_txts']
        if temp:
            line_out['admin_notes'] = temp

        temp = {}
        if 'title_en_txts' in line and line['title_en_txts']:
            temp[u'en'] = line['title_en_txts']
        if 'title_fr_txts' in line and line['title_fr_txts']:
            temp[u'fr'] = line['title_fr_txts']
        if temp:
            line_out['title'] = temp

        temp = {}
        if 'description_en_txts' in line and line['description_en_txts']:
            temp[u'en'] = line['description_en_txts']
        if 'description_fr_txts' in line and line['description_fr_txts']:
            temp[u'fr'] = line['description_fr_txts']
        if temp:
            line_out['notes'] = temp

        if 'conttypecode_bi_txtm' in line:
            result = listify(line['conttypecode_bi_txtm'])
            if result:
                line_out['content_type_codes'] = result

        if 'dispandtrack_bi_txtm' in line:
            result = code_lookup('dispandtrack_bi_txtm', line, tracking_list)
            if result:
                line_out['tracking_codes'] = result

        if 'geolevel_en_txtm' in line:
            result = code_lookup('geolevel_en_txtm', line, geolevel_list)
            if result:
                line_out['geolevel_codes'] = result

        # if 'specificgeo_en_txtm' in line:
        #     result = code_lookup('specificgeo_en_txtm', line, geodescriptor_list)
        #     if result:
        #         line_out['geodescriptor_codes'] = result

        if 'subjnew_en_txtm' in line:
            result = code_lookup('subjnew_en_txtm', line, subject_list)
            if result:
                line_out['subject_codes'] = result

        if 'related_bi_strm' in line and line['related_bi_strm']:
            result =  listify(line['related_bi_strm'])
            if result:
                line_out['related_products'] = result

        temp = {}
        if 'stcthesaurus_en_txtm' in line:
            result = listify(line['stcthesaurus_en_txtm'])
            if result:
                temp[u'en'] = result
        if 'stcthesaurus_fr_txtm' in line:
            result = listify(line['stcthesaurus_fr_txtm'])
            if result:
                temp[u'fr'] = result
        if temp:
            line_out['thesaurus'] = temp

        if 'archivedate_bi_txts' in line and line['archivedate_bi_txts']:
            line_out['archive_date'] = line['archivedate_bi_txts']

        if 'archived_bi_strs' in line:
            result =  code_lookup('archived_bi_strs', line, archive_status_list)
            if result:
                line_out['archive_status_code'] = result[0]

        # if 'defaultviewid_bi_strs' and line['defaultviewid_bi_strs']:
        #     line_out['default_view_id'] = line['defaultviewid_bi_strs']

        if 'dimmembers_en_txtm':
            result = code_lookup('dimmembers_en_txtm', line, dimension_member_list)
            if result:
                line_out['dimension_member_codes'] = result

        if 'display_en_txtm' in line:
            result = code_lookup('display_en_txtm', line, display_list)
            if result:
                line_out['display_code'] = result

        if 'frccode_bi_strs' in line and line['frccode_bi_strs']:
            line_out['frc'] = line['frccode_bi_strs']

        if 'freq_en_txtm' in line:
            result = code_lookup('freq_en_txtm', line, frequency_list)
            if result:
                line_out['frequency_codes'] = result

        if 'hierarchyid_bi_strm' in line:
            result = listify(line['hierarchyid_bi_strm'])
            if result:
                line_out['parent_product'] = result[0]

        temp = {}
        if 'histnotes_en_txts' in line and line['histnotes_en_txts']:
            temp[u'en'] = line['histnotes_en_txts']
        if 'histnotes_fr_txts' in line and line['histnotes_fr_txts']:
            temp[u'fr'] = line['histnotes_fr_txts']
        if temp:
            line_out['history_notes'] = temp

        if 'interncontactname_bi_txts' and line['interncontactname_bi_txts']:
            result = listify(line['interncontactname_bi_txts'])
            if result:
                line_out['internal_contacts'] = result

        temp = {}
        if 'keywordsuncon_en_txtm' in line:
            result = listify(line['keywordsuncon_en_txtm'])
            if result:
                temp[u'en'] = result
        if 'keywordsuncon_fr_txtm':
            result = listify(line['keywordsuncon_fr_txtm'])
            if result:
                temp[u'fr'] = result
        if temp:
            line_out['keywords'] = temp

        if 'lastpublishstatus_en_strs' in line:
            result =  code_lookup('lastpublishstatus_en_strs', line, publish_list)
            if result:
                line_out['last_publish_status_code'] = result[0]

        if 'productidnew_bi_strs' in line and line['productidnew_bi_strs']:
            line_out['product_id_new'] = line['productidnew_bi_strs']
            line_out['name'] = 'publication-{0}'.format(line['productidnew_bi_strs'])

        if 'productidold_bi_strs' in line and line['productidold_bi_strs']:
            line_out['product_id_old'] = line['productidold_bi_strs']

        temp = {}
        if 'refperiod_en_txtm' in line:
            result = listify(line['refperiod_en_txtm'])
            if result:
                temp[u'en'] = result
        if 'refperiod_fr_txtm' in line:
            result = listify(line['refperiod_fr_txtm'])
            if result:
                temp[u'fr'] = result
        if temp:
            line_out['reference_periods'] = temp

        if 'releasedate_bi_strs' in line and line['releasedate_bi_strs']:
            line_out['release_date'] = line['releasedate_bi_strs']

        if 'replaces_bi_strm' in line:
            result = listify(line['replaces_bi_strm'])
            if result:
                line_out['replaced_products'] = result

        if 'sourcecode_bi_txtm' in line and line['sourcecode_bi_txtm']:
            result = listify(line['sourcecode_bi_txtm'])
            if result:
                line_out['survey_source_codes'] = result

        if 'statusf_en_strs' in line:
            result = code_lookup('statusf_en_strs', line, status_list)
            if result:
                line_out['status_codes'] = result

        temp = {}
        if 'url_en_strs' in line and line['url_en_strs']:
            temp[u'en'] = line['url_en_strs']
        if 'url_fr_strs' in line and line['url_fr_strs']:
            temp[u'fr'] = line['url_fr_strs']
        if temp:
            line_out['url'] = temp

        print json.dumps(line_out)
