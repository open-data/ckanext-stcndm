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
            sys.stderr.write(u'resource-{0}: weird {1} .{2}.{3}.\n'.format(line['product_id_new'], old_field_name,
                                                                           _temp, field_value))
        else:
            codes.append(code)
    return codes

rc = ckanapi.RemoteCKAN('http://127.0.0.1')

content_type_list = []
geolevel_list = []
frequency_list = []
status_list = []
display_list = []
tracking_list = []
publish_list = []

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
    if preset['preset_name'] == 'ndm_format':
        format_list = preset['values']['choices']
        if not format_list:
            raise ValueError('could not find format preset')
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
    rc = ckanapi.RemoteCKAN('http://127.0.0.1/')
    query_results = rc.action.package_search(
        q='type:issue',
        rows=1000,
        start=i*1000)

    count = 0
    for line in query_results['results']:

        rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj/')

        formats = rc.action.package_search(
            q='extras_productidnew_bi_strs:{0}'.format(line['product_id_new']),
            rows=1000,
            start=i*1000)

        resources_out = []

        for resource in formats['results']:

            for e in resource['extras']:
                resource[e['key']] = e['value']

            resource_dict = {u'name': resource['name']}

            temp = {}
            if 'adminnotes_bi_txts' in resource and resource['adminnotes_bi_txts']:
                temp[u'en'] = resource['adminnotes_bi_txts']
                temp[u'fr'] = resource['adminnotes_bi_txts']
            if temp:
                resource_dict['admin_notes'] = temp
            else:
                resource_dict['admin_notes'] = {'en': '',
                                                'fr': ''}

            if 'isbnnum_bi_strs' in resource and resource['isbnnum_bi_strs']:
                resource_dict['isbn_number'] = resource['isbnnum_bi_strs']
            else:
                resource_dict['isbn_number'] = ''

            if 'releasedate_bi_strs' in resource and resource['releasedate_bi_strs']:
                resource_dict['release_date'] = resource['releasedate_bi_strs']
            else:
                resource_dict['release_date'] = ''

            if 'formatcode_bi_txtm' in resource and resource['formatcode_bi_txtm']:
                resource_dict['format_code'] = listify(resource['formatcode_bi_txtm'].zfill(2))
            else:
                resource_dict['format_code'] = ''

            # if 'formatcode_bi_txtm' in resource:
            #     result = code_lookup('formatcode_bi_txtm', resource, format_list)
            #     if result:
            #         resource_dict['format_code'] = result
            #     else:
            #         resource_dict['format_code'] = ''

            if 'display_bi_txtm' in line:
                result = code_lookup('display_bi_txtm', line, display_list)
                if result:
                    resource_dict['display_code'] = result
                else:
                    resource_dict['display_code'] = '1'
            else:
                resource_dict['display_code'] = '1'

            if 'dispandtrack_bi_txtm' in line:
                result = code_lookup('dispandtrack_bi_txtm', line, tracking_list)
                if result:
                    resource_dict['tracking_codes'] = result
                else:
                    resource_dict['tracking_codes'] = '01'
            else:
                resource_dict['tracking_codes'] = '01'

            if 'lastpublishstatus_en_strs' in resource:
                result = code_lookup('lastpublishstatus_en_strs', resource, publish_list)
                if result:
                    resource_dict['last_publish_status_code'] = result[0]
                else:
                    resource_dict['last_publish_status_code'] = ''

            if 'statusf_en_strs' in resource:
                result = code_lookup('statusf_en_strs', resource, status_list)
                if result:
                    resource_dict['status_codes'] = result
            else:
                resource_dict['status_codes'] = ''

            if 'url_en_strs' in resource and resource['url_en_strs']:
                resource_dict['url_en'] = resource['url_en_strs']

            if 'url_fr_strs' in resource and resource['url_fr_strs']:
                resource_dict['url_fr'] = resource['url_fr_strs']

            # TODO: The schema includes correction ID here but I'm 95% sure it's not needed, omitting for now

            resources_out.append(resource_dict)

            line['resources'] = resources_out

            print json.dumps(line)
            ckanapi_update = ckanapi.RemoteCKAN('http://127.0.0.1',
                                                apikey='API_KEY')

            try:
                result = ckanapi_update.action.resource_create(package_id=line['id'],
                                                               name='{0}-{1}-en'.format(line['name'],
                                                               resource_dict[u'format_code'][0]),
                                                               language='en',
                                                               admin_notes=resource_dict[u'admin_notes']['en'],
                                                               isbn_number=resource_dict[u'isbn_number'],
                                                               release_date=resource_dict[u'release_date'],
                                                               format_code=resource_dict[u'format_code'],
                                                               display_code=resource_dict[u'display_code'],
                                                               tracking_codes=resource_dict[u'tracking_codes'],
                                                               last_publish_status_code=resource_dict[u'last_publish_status_code'],
                                                               status_codes=resource_dict[u'status_codes'],
                                                               url=resource_dict[u'url_en'],
                                                               type='html'
                                                               )

                result = ckanapi_update.action.resource_create(package_id=line['id'],
                                                               name='{0}-{1}-fr'.format(line['name'],
                                                               resource_dict[u'format_code'][0]),
                                                               language='fr',
                                                               admin_notes=resource_dict[u'admin_notes']['fr'],
                                                               isbn_number=resource_dict[u'isbn_number'],
                                                               release_date=resource_dict[u'release_date'],
                                                               format_code=resource_dict[u'format_code'],
                                                               display_code=resource_dict[u'display_code'],
                                                               tracking_codes=resource_dict[u'tracking_codes'],
                                                               last_publish_status_code=resource_dict[u'last_publish_status_code'],
                                                               status_codes=resource_dict[u'status_codes'],
                                                               url=resource_dict[u'url_fr'],
                                                               type='html'
                                                               )
            except:
                pass

            count += 1

    print count
