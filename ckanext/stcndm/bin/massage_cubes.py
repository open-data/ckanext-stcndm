__author__ = 'marc'

import sys
import json
import yaml
import ckanapi


def in_and_def(key, a_dict):
    if key in a_dict and a_dict[key]:
        return True
    else:
        return False


def listify(value):
    if isinstance(value, unicode):
        return filter(None, map(unicode.strip, value.split(';')))  # filter removes empty strings
    elif isinstance(value, list):
        return filter(None, map(unicode.strip, value[0].split(';')))
    else:
        return []


def code_lookup(table_name, value, data_dict):
    field_values = listify(value.lower())
    codes = []
    for field_value in field_values:
        if '|' in field_value:
            (field_value, bogon) = field_value.split('|', 1)
            field_value = field_value.strip()
        if field_value in code_lookup_dict[table_name]:
            codes.append(code_lookup_dict[table_name][field_value])
        else:
            sys.stderr.write(
                'cube-{0}: weird {1} .{2}.\n'.format(data_dict['productidnew_bi_strs'], table_name, field_value)
            )
    return codes


rc = ckanapi.RemoteCKAN('http://127.0.0.1:5000')

code_lookup_dict = {
    'content_type': {},
    'geolevel': {},
    'frequency': {}
}

i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='type:codeset',
        rows=1000,
        start=i*1000)
    i += 1
    n = query_results['count'] / 1000.0
    for codeset in query_results['results']:
        if in_and_def('title', codeset) and in_and_def('codeset_value', codeset):
            try:
                code_lookup_dict[codeset['codeset_type']][codeset['title']['en'].lower().strip()] = \
                    codeset['codeset_value']
            except KeyError:
                pass

code_lookup_dict['subject'] = {}
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='type:subject',
        rows=1000,
        start=i*1000)
    i += 1
    n = query_results['count'] / 1000.0
    for result in query_results['results']:
        if in_and_def('title', result) and in_and_def('subject_code', result):
            code_lookup_dict['subject'][result['title']['en'].lower().strip()] = result['subject_code']

code_lookup_dict['geodescriptor'] = {}
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='type:geodescriptor',
        rows=1000,
        start=i*1000)
    i += 1
    n = query_results['count'] / 1000.0
    for result in query_results['results']:
        if in_and_def('title', result) and in_and_def('geodescriptor_code', result):
            code_lookup_dict['geodescriptor'][result['title']['en'].lower().strip()] = result['geodescriptor_code']

code_lookup_dict['dimension_member'] = {}
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='type:dimension_member',
        rows=1000,
        start=i*1000)
    i += 1
    n = query_results['count'] / 1000.0
    for result in query_results['results']:
        if in_and_def('title', result) and in_and_def('dimension_member_code', result):
            code_lookup_dict['dimension_member'][result['title']['en'].lower().strip()] = \
                result['dimension_member_code']

code_lookup_dict['survey'] = {}
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='type:survey',
        rows=1000,
        start=i*1000)
    i += 1
    n = query_results['count'] / 1000.0
    for result in query_results['results']:
        if in_and_def('title', result) and in_and_def('product_id_new', result):
            code_lookup_dict['survey'][result['title']['en'].lower().strip()] = result['product_id_new']

f = open('../schemas/presets.yaml')
presetMap = yaml.safe_load(f)
f.close()
for preset in presetMap['presets']:
    if preset['preset_name'] == 'ndm_archive_status':
        code_lookup_dict['archive_status'] = {}
        for choice in preset['values']['choices']:
            code_lookup_dict['archive_status'][choice['label']['en'].lower().strip()] = choice['value']
    if preset['preset_name'] == 'ndm_collection_methods':
        code_lookup_dict['collection_method'] = {}
        for choice in preset['values']['choices']:
            code_lookup_dict['collection_method'][choice['label']['en'].lower().strip()] = choice['value']
    if preset['preset_name'] == 'ndm_survey_status':
        code_lookup_dict['survey_status'] = {}
        for choice in preset['values']['choices']:
            code_lookup_dict['survey_status'][choice['label']['en'].lower().strip()] = choice['value']
    if preset['preset_name'] == 'ndm_survey_participation':
        code_lookup_dict['survey_participation'] = {}
        for choice in preset['values']['choices']:
            code_lookup_dict['survey_participation'][choice['label']['en'].lower().strip()] = choice['value']
    if preset['preset_name'] == 'ndm_survey_owner':
        code_lookup_dict['survey_owner'] = {}
        for choice in preset['values']['choices']:
            code_lookup_dict['survey_owner'][choice['label']['en'].lower().strip()] = choice['value']
    # if preset['preset_name'] == 'ndm_format':
    #    code_lookup_dict['format'] = {}
    #    for choice in preset['values']['choices']:
    #        code_lookup_dict['format'][choice['label']['en'].lower().strip()] = choice['value']
    if preset['preset_name'] == 'ndm_tracking':
        code_lookup_dict['tracking'] = {}
        for choice in preset['values']['choices']:
            code_lookup_dict['tracking'][choice['label']['en'].lower().strip()] = choice['value']
    if preset['preset_name'] == 'ndm_display':
        code_lookup_dict['display'] = {}
        for choice in preset['values']['choices']:
            code_lookup_dict['display'][choice['label']['en'].lower().strip()] = choice['value']
    if preset['preset_name'] == 'ndm_publish_status':
        code_lookup_dict['publish_status'] = {}
        for choice in preset['values']['choices']:
            code_lookup_dict['publish_status'][choice['label']['en'].lower().strip()] = choice['value']
    if preset['preset_name'] == 'ndm_status':
        code_lookup_dict['status'] = {}
        for choice in preset['values']['choices']:
            code_lookup_dict['status'][choice['label']['en'].lower().strip()] = choice['value']
    if preset['preset_name'] == 'ndm_subject_display':
        code_lookup_dict['subject_display'] = {}
        for choice in preset['values']['choices']:
            code_lookup_dict['subject_display'][choice['label']['en'].lower().strip()] = choice['value']

rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj/')
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='organization:rgcube',
        rows=1000,
        start=i*1000)
    i += 1
    n = query_results['count'] / 1000.0
    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        line_out = {u'owner_org': u'statcan',
                    u'private': False,
                    u'type': u'cube',
                    u'product_type_code': u'10'}

        temp = {}
        if in_and_def('adminnotes_bi_txts', line):
            temp[u'en'] = line['adminnotes_bi_txts']
            temp[u'fr'] = line['adminnotes_bi_txts']
        if temp:
            line_out['admin_notes'] = temp

        temp = {}
        if in_and_def('title_en_txts', line):
            temp[u'en'] = line['title_en_txts']
        if in_and_def('title_fr_txts', line):
            temp[u'fr'] = line['title_fr_txts']
        if temp:
            line_out['title'] = temp

        temp = {}
        if in_and_def('description_en_txts', line):
            temp[u'en'] = line['description_en_txts']
        if in_and_def('description_fr_txts', line):
            temp[u'fr'] = line['description_fr_txts']
        if temp:
            line_out['notes'] = temp

        if in_and_def('conttypecode_bi_txtm', line):
            result = listify(line['conttypecode_bi_txtm'])
            if result:
                line_out['content_type_codes'] = result

        if in_and_def('dispandtrack_bi_txtm', line):
            result = code_lookup('tracking', line['dispandtrack_bi_txtm'], line)
            if result:
                line_out['tracking_codes'] = result

        if in_and_def('geolevel_en_txtm', line):
            result = code_lookup('geolevel', line['geolevel_en_txtm'], line)
            if result:
                line_out['geolevel_codes'] = result

        if in_and_def('specificgeocode_bi_txtm', line):
            result = listify(line['specificgeocode_bi_txtm'])
            if result:
                line_out['geodescriptor_codes'] = result
        if 'geodescriptor_codes' not in line_out and in_and_def('specificgeo_en_txtm', line):
            result = code_lookup('geodescriptor', line['specificgeo_en_txtm'], line)
            if result:
                line_out['geodescriptor_codes'] = result

        if in_and_def('subjnewcode_bi_txtm', line):
            result = listify(line['subjnewcode_bi_txtm'])
            if result:
                line_out['subject_codes'] = result
        if 'subject_codes' not in line_out and in_and_def('subjnew_en_txtm', line):
            result = code_lookup('subject', line['subjnew_en_txtm'], line)
            if result:
                line_out['subject_codes'] = result

        if in_and_def('related_bi_strm', line):
            result = listify(line['related_bi_strm'])
            if result:
                line_out['related_products'] = result

        temp = {}
        if in_and_def('stcthesaurus_en_txtm', line):
            result = listify(line['stcthesaurus_en_txtm'])
            if result:
                temp[u'en'] = result
        if in_and_def('stcthesaurus_fr_txtm', line):
            result = listify(line['stcthesaurus_fr_txtm'])
            if result:
                temp[u'fr'] = result
        if temp:
            line_out['thesaurus'] = temp

        if in_and_def('archivedate_bi_txts', line):
            line_out['archive_date'] = line['archivedate_bi_txts']

        if in_and_def('archived_bi_strs', line):
            result = code_lookup('archive_status', line['archived_bi_strs'], line)
            if result:
                line_out['archive_status_code'] = result[0]

        if in_and_def('defaultviewid_bi_strs', line):
            line_out['default_view_id'] = line['defaultviewid_bi_strs']

        if in_and_def('dimmembers_en_txtm', line):
            result = code_lookup('dimension_member', line['dimmembers_en_txtm'], line)
            if result:
                line_out['dimension_member_codes'] = result

        if in_and_def('display_en_txtm', line):
            result = code_lookup('display', line['display_en_txtm'], line)
            if result:
                line_out['display_code'] = result

        if in_and_def('frccode_bi_strs', line):
            line_out['frc'] = line['frccode_bi_strs']

        if in_and_def('freq_en_txtm', line):
            result = code_lookup('frequency', line['freq_en_txtm'], line)
            if result:
                line_out['frequency_codes'] = result

        # if in_and_def('hierarchyid_bi_strm', line):
        #     result = listify(line['hierarchyid_bi_strm'])
        #     if result:
        #         line_out['parent_product'] = result[0]
        #
        # if in_and_def('hierarchyid_bi_strs', line):
        #     result = listify(line['hierarchyid_bi_strs'])
        #     if result:
        #         line_out['parent_product'] = result[0]

        if in_and_def('10uid_bi_strs', line):
            line_out['parent_product'] = line['10uid_bi_strs']

        temp = {}
        if in_and_def('histnotes_en_txts', line):
            temp[u'en'] = line['histnotes_en_txts']
        if in_and_def('histnotes_fr_txts', line):
            temp[u'fr'] = line['histnotes_fr_txts']
        if temp:
            line_out['history_notes'] = temp

        if in_and_def('interncontactname_bi_txts', line):
            result = listify(line['interncontactname_bi_txts'])
            if result:
                line_out['internal_contacts'] = result

        temp = {}
        if in_and_def('keywordsuncon_en_txtm', line):
            result = listify(line['keywordsuncon_en_txtm'])
            if result:
                temp[u'en'] = result
        if in_and_def('keywordsuncon_fr_txtm', line):
            result = listify(line['keywordsuncon_fr_txtm'])
            if result:
                temp[u'fr'] = result
        if temp:
            line_out['keywords'] = temp

        if in_and_def('lastpublishstatus_en_strs', line):
            result = code_lookup('publish_status', line['lastpublishstatus_en_strs'], line)
            if result:
                line_out['last_publish_status_code'] = result[0]

        if in_and_def('productidnew_bi_strs', line):
            line_out['product_id_new'] = line['productidnew_bi_strs']
            line_out['name'] = 'cube-{0}'.format(line['productidnew_bi_strs'].lower())

        if in_and_def('productidold_bi_strs', line):
            line_out['product_id_old'] = line['productidold_bi_strs']

        temp = {}
        if in_and_def('refperiod_en_txtm', line):
            result = listify(line['refperiod_en_txtm'])
            if result:
                temp[u'en'] = result
        if in_and_def('refperiod_fr_txtm', line):
            result = listify(line['refperiod_fr_txtm'])
            if result:
                temp[u'fr'] = result
        if temp:
            line_out['reference_periods'] = temp

        if in_and_def('releasedate_bi_strs', line):
            line_out['release_date'] = line['releasedate_bi_strs']

        if in_and_def('replaces_bi_strm', line):
            result = listify(line['replaces_bi_strm'])
            if result:
                line_out['replaced_products'] = result

        if in_and_def('sourcecode_bi_txtm', line):
            result = listify(line['sourcecode_bi_txtm'])
            if result:
                line_out['survey_source_codes'] = result

        if in_and_def('statusf_en_strs', line):
            result = code_lookup('status', line['statusf_en_strs'], line)
            if result:
                line_out['status_codes'] = result[0]

        temp = {}
        if in_and_def('url_en_strs', line):
            temp[u'en'] = line['url_en_strs']
        if in_and_def('url_fr_strs', line):
            temp[u'fr'] = line['url_fr_strs']
        if temp:
            line_out['url'] = temp

        if 'resources' in line:
            line_out['resources'] = line['resources']

        if 'num_resources' in line:
            line_out['num_resources'] = line['num_resources']

        if 'license_title' in line:
            line_out['license_title'] = line['license_title']

        if 'license_url' in line:
            line_out['license_url'] = line['license_url']

        if 'license_id' in line:
            line_out['license_id'] = line['license_id']

        print json.dumps(line_out)
